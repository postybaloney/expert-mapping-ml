from app.summarizer import summarize_expert
from app.graph import ingest_profiles
from tqdm import tqdm

# usernames = ["karpathy", "lucidrains", "3494126"]
# for user in tqdm(usernames):
#     summarize_expert(user)

ingest_profiles("data/raw")