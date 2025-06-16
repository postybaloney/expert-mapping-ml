from neo4j import GraphDatabase
import json
from pathlib import Path
import os
from dotenv import load_dotenv
import openai
import random
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

openai.api_key = os.getenv("OPENAI_API_KEY")

def embed_profile(profile):
    # text = profile['expertise'] + " " + " ".join(profile['top_skills'])
    # response = openai.embeddings.create(input=[text], model="text-embedding-3-small")
    # return response.data[0].embedding
    return [random.random() for _ in range(1536)]

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
driver.verify_connectivity()

def load_profile(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)
        if isinstance(raw, str):
            print("Issue with profile format, trying to parse as JSON")
            return json.loads(raw)
        return raw
    
def create_expert(tx, username, profile, vector):
    tx.run("""
           MERGE (e:Expert {username: $username})
           Set e.expertise = $expertise
           Set e.vector = $vector
           """, username=username, expertise=profile['expertise'], vector = vector)
    
    tx.run("""
        MATCH (e:Expert {username: $username})
        WITH e,
         COUNT { (e)-[:CONTRIBUTED_TO]->() } AS contribution_count,
         COUNT { (e)-[:HAS_SKILL]->() } AS skill_count
        SET e.experience_level = CASE
            WHEN contribution_count >= 10 THEN 'senior'
            WHEN contribution_count >= 5 THEN 'mid-level'
            ELSE 'junior'
        END,
        e.project_count = contribution_count,
        e.skill_count = skill_count
    """, username=username)
    
    for skill in profile['top_skills']:
        tx.run("""
               MERGE (s:Skill {name: $skill})
                MERGE (e:Expert {username: $username})
               MERGE (e)-[:HAS_SKILL] -> (s)
               """, username=username, skill=skill)
        
    for contribution in profile['notable_contributions']:
        if contribution['url']:
            tx.run("""
                MERGE (p:Project {name: $name, url: $url})
                MERGE (e:Expert {username: $username})
                Merge (e)-[:CONTRIBUTED_TO]->(p)
                """, username=username, name=contribution['project'], url=contribution['url'])
        
def ingest_profiles(data_dir):
    for path in Path(data_dir).glob("*_profile.json"):
        username = path.stem.replace("_profile", "")
        profile = load_profile(path)
        vector = embed_profile(profile)
        with driver.session() as session:
            session.execute_write(create_expert, username, profile, vector)
        print(f"Ingested profile for {username}")

if __name__ == "__main__":
    ingest_profiles("data/raw")

driver.close()