from fastapi import FastAPI, HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os, re
from openai import OpenAI
import numpy as np
from numpy.linalg import norm
import traceback
from typing import Optional
load_dotenv()

app = FastAPI()
# router = AP
client = OpenAI()

def embed_query(text: str):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding



def cosine_similarity(a, b):
    # simple runtime cosine similarity
    return np.dot(a,b) / (norm(a)* norm(b))

def highlight(text, terms):
    pattern = re.compile("(" + "|".join(re.escape(t) for t in terms) + ")", re.IGNORECASE)
    return pattern.sub(r"<b>\1</b>", text)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

@app.get("/experts/by-skill/{skill_name}")
def get_experts_by_skill(skill_name: str):
    with driver.session() as session:
        result = session.run("""
            MATCH (e:Expert)-[:HAS_SKILL]->(s:Skill {name: $skill_name})
            RETURN e.username AS username, e.expertise AS expertise
        """, skill_name=skill_name)
        experts = [record.data() for record in result]
        if not experts:
            raise HTTPException(status_code=404, detail="No experts found with this skill")
        return {"skill": skill_name, "experts": experts}

@app.get("/experts/{username}/projects")
def get_expert_projects(username: str):
    with driver.session() as session:
        result = session.run("""
            MATCH (e:Expert {username: $username})-[:CONTRIBUTED_TO]->(p:Project)
            RETURN p.name AS project_name, p.url AS project_url
        """, username=username)
        projects = [record.data() for record in result]
        if not projects:
            raise HTTPException(status_code=404, detail="No projects found for this expert")
        return {"username": username, "projects": projects}
    
@app.get("/experts/{username}/skills")
def get_expert_skills(username: str):
    with driver.session() as session:
        result = session.run("""
            MATCH (e:Expert {username: $username})-[:HAS_SKILL]->(s:Skill)
            RETURN s.name AS skill_name
        """, username=username)
        skills = [record.data() for record in result]
        if not skills:
            raise HTTPException(status_code=404, detail="No skills found for this expert")
        return {"username": username, "skills": skills}
    
@app.get("/experts")
def get_all_experts():
    with driver.session() as session:
        result = session.run("""
            MATCH (e:Expert)
            RETURN e.username AS username, e.expertise AS expertise
        """)
        experts = [record.data() for record in result]
        if not experts:
            raise HTTPException(status_code=404, detail="No experts found")
        return {"experts": experts}
    
@app.get("/skills")
def get_all_skills():
    with driver.session() as session:
        result = session.run("""
            MATCH (s:Skill)
            RETURN s.name AS skill_name
        """)
        skills = [record.data() for record in result]
        if not skills:
            raise HTTPException(status_code=404, detail="No skills found")
        return {"skills": skills}

@app.get("/projects")
def get_all_projects():
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Project)
            RETURN p.name AS project_name, p.url AS project_url
        """)
        projects = [record.data() for record in result]
        if not projects:
            raise HTTPException(status_code=404, detail="No projects found")
        return {"projects": projects}
    
@app.get("/experts/{username}")
def get_expert_profile(username: str):
    with driver.session() as session:
        result = session.run("""
            MATCH (e:Expert {username: $username})
            RETURN e.username AS username, e.expertise AS expertise, e.top_skills AS top_skills, e.notable_contributions AS notable_contributions
        """, username=username)
        profile = result.single()
        if not profile:
            raise HTTPException(status_code=404, detail="Expert not found")
        return profile.data()

@app.post("/search")
def search_experts(query: str, page: int = 1, page_size: int = 10, filter_skill: Optional[str] = None, experience: Optional[str] = None, sort_by: Optional[str] = None): # Experience takes junior, mid-level, senior, Sort_by takes project_count, skill_count
    try:
        q_emb = embed_query(query)
        offset = (page - 1) * page_size

        allowed_sort_fields = {"exp_score", "skill_count", "project_count"}
        sort_field = sort_by if sort_by in allowed_sort_fields else "exp_score"

        where_clauses = ["id(e) = id(node)"]
        if filter_skill:
            where_clauses.append("EXISTS {MATCH (e)-[:HAS_SKILL]->(s:Skill {name: $filter_skill}) }")
        if experience:
            where_clauses.append("e.experience_level = $experience")
        where_block = "WHERE " + " AND ".join(where_clauses)

        with driver.session() as session:
            results = session.run(
                f"""
                CALL db.index.vector.queryNodes('expert_vector_index', $k, $embedding)
                YIELD node, score
                MATCH (e:Expert)
                {where_block}
                WITH e, 
                    node,
                    score,
                    size([ (e)-[:HAS_SKILL]->(s) | s ]) AS skill_count,
                    size([ (e)-[:CONTRIBUTED_TO]->(p) | p ]) AS project_count
                RETURN 
                    node.username as username,
                    node.expertise as expertise,
                    node.vector as vector,
                    [ (node)-[:HAS_SKILL]->(s) | s.name ] as skills,
                    [ (node)-[:CONTRIBUTED_TO]->(p) | {{name: p.name, description: p.description, url: p.url, vector: p.vector}} ] as projs,
                    score as exp_score
                ORDER BY {sort_field} DESC
                SKIP $offset
                LIMIT $limit
                """,
                {
                    "k": 100, # Search depth, k-nearest neighbors
                    "embedding": q_emb,
                    "offset": offset,
                    "limit": page_size,
                    "filter_skill": filter_skill,
                    "experience": experience
                }
            )
            hits = []
            for rec in results:
                skills = rec.get("skills", [])
                projects = rec.get("projs", [])
                
                # 2. Skill filtering/matching
                matched_skills = [s for s in skills if any(tok.lower() in s.lower() for tok in query.split())]

                # 3. Project ranking
                proj_list = []
                for p in projects:
                    if not isinstance(p, dict):
                        print(p, "is not a dict, skipping")
                        continue
                    desc = p["description"] or ""
                    name = p["name"]
                    p_emb = p.get("vector")
                    proj_score = cosine_similarity(q_emb, p_emb) if p_emb else 0
                    proj_list.append({"name": name, "description": desc, "url": p["url"], "proj_score": proj_score})
                proj_list.sort(key=lambda x: x["proj_score"], reverse=True)
                proj_list = proj_list[:5]  # top 5 projects

                # 4. Highlight terms
                query_terms = query.split()
                matched_skills = [highlight(s, query_terms) for s in matched_skills]
                for p in proj_list:
                    p["name"] = highlight(p["name"], query_terms)
                    p["description"] = highlight(p["description"], query_terms)

                hits.append({
                    "username": rec["username"],
                    "score": rec["exp_score"],
                    "matched_skills": matched_skills,
                    "matched_projects": proj_list
                })

        if not hits:
            raise HTTPException(status_code=404, detail="No experts found")
        return {
            "query": query,
            "page": page,
            "page_size": page_size,
            "results": hits
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/expert/{username}/similar")
def get_similar_experts(username: str, k: int = 5):
    try:
        with driver.session() as session:
            # Get the expert's vector
            result = session.run("""
                MATCH (e:Expert {username: $username})
                RETURN e.vector AS vector
            """, username=username)
            expert = result.single()
            if not expert:
                raise HTTPException(status_code=404, detail="Expert not found")
            expert_vector = expert["vector"]

            # Find similar experts
            results = session.run("""
                CALL db.index.vector.queryNodes('expert_vector_index', $k, $embedding)
                YIELD node, score
                MATCH (e:Expert) WHERE id(e) = id(node)
                RETURN e.username AS username, e.expertise AS expertise, score AS similarity_score
            """, k=k, embedding=expert_vector)

            similar_experts = [record.data() for record in results]
            if not similar_experts:
                raise HTTPException(status_code=404, detail="No similar experts found")
            return {"username": username, "similar_experts": similar_experts}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
