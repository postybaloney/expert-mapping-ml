from app.summarizer import summarize_expert
from app.graph import ingest_profiles
from app.scrapper import web_scraper
from app.collector import file_creation_json
from app.summarizer import profile_creation
from tqdm import tqdm
from fastapi import FastAPI
from app.api import app as api_app
from app.api import app

web_scraper()
file_creation_json()
profile_creation()
ingest_profiles("data/raw")

app = FastAPI()
app.include_router(api_app)