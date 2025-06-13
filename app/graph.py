from neo4j import GraphDatabase
import json
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
driver.verify_connectivity()

def load_profile(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)
        if isinstance(raw, str):
            return json.loads(raw)
        return raw
    
def create_expert(tx, username, profile):
    tx.run("""
           MERGE (e:Expert {username: $username})
           Set e.expertise = $expertise
           """, username=username, expertise=profile['expertise'])
    
    for skill in profile['top_skills']:
        tx.run("""
               MERGE (s:Skill {name: $skill})
                MERGE (e:Expert {username: $username})
               MERGE (e)-[:HAS_SKILL] -> (s)
               """, username=username, skill=skill)
        
    for contribution in profile['notable_contributions']:
        tx.run("""
               MERGE (p:Project {name: $name, url: $url})
               MERGE (e:Expert {username: $username})
               Merge (e)-[:CONTRIBUTED_TO]->(p)
               """, username=username, name=contribution['project'], url=contribution['url'])
        
def ingest_profiles(data_dir):
    for path in Path(data_dir).glob("*_profile.json"):
        username = path.stem.replace("_profile", "")
        profile = load_profile(path)
        with driver.session() as session:
            session.execute_write(create_expert, username, profile)
        print(f"Ingested profile for {username}")

if __name__ == "__main__":
    ingest_profiles("data/raw")

driver.close()