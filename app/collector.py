import requests
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
load_dotenv()

DATA_DIR = Path("data/raw")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Optional: Set your GitHub token as an environment variable
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")  # Optional: Set your RapidAPI key as an environment variable
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")  # Optional: Set your RapidAPI host as an environment variable

ML_KEYWORDS = [
    "machine learning", "deep learning", "artificial intelligence",
    "neural networks", "computer vision", "natural language processing",
    "reinforcement learning", "data science", "big data", "AI ethics", "transformers", "transformer", 
    "GPT", "BERT", "PyTorch", "TensorFlow", "Keras", "scikit-learn",
    "huggingface", "gradient descent", "backpropagation", "convolutional neural networks",
    "recurrent neural networks", "LSTM", "GANs", "autoencoders", "unsupervised learning"]

def is_ml_keyword(keyword: str) -> bool:
    """
    Check if a keyword is related to machine learning.
    """
    return any(ml_keyword in keyword.lower() for ml_keyword in ML_KEYWORDS)

with open("ml_expert_sources.json", "r", encoding="utf-8") as f:
    expert_sources = json.load(f)

GITHUB_USERS = expert_sources['github_users']
STACKOVERFLOW_USERS = expert_sources['stackoverflow_users']
BLOG_AUTHORS = expert_sources['blog_authors']

def fetch_github_user_repos(username, token=None):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {"Authorization": f"token {token}"} if token else {}
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_github_repo_commits(username, repo_name, token=None):
    url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
    headers = {"Authorization": f"token {token}"} if token else {}
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_stackoverflow_answers(user_id):
    url = f"https://api.stackexchange.com/2.3/users/{user_id}/answers?order=desc&sort=activity&site=stackoverflow&filter=withbody"
    response = requests.get(url)
    return response.json()

def fetch_medium_articles(username):
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST} if RAPIDAPI_KEY and RAPIDAPI_HOST else {}
    user_id = requests.get(f"https://medium2.p.rapidapi.com/user/id_for/{username}", headers=headers).json()['id']
    response = requests.get(f"https://medium2.p.rapidapi.com/user/{user_id}/top_articles", headers=headers)
    if response.status_code == 200:
        top_articles = response.json().get("top_articles", [])
        if not top_articles:
            print(f"No articles found for {username}")
            return []
        else:
            all_articles = []
            for article in top_articles:
                article_resp = requests.get(f"https://medium2.p.rapidapi.com/article/{article}", headers=headers)
                if article_resp.status_code == 200:
                    article_data = article_resp.json()
                    all_articles.append(article_data)
            # print([{
            #     "title": art["title"],
            #     "url": art["url"],
            #     "published": art["published_at"],
            #     "tags": [tag.replace("-", " ") for tag in art['tags']],
            #     "topics": [tag.replace("-", " ") for tag in art['topics']]
            # } for art in all_articles])
            return [{
                "title": art["title"],
                "url": art["url"],
                "published": art.get("published_at"),
                "tags": [tag.replace("-", " ") for tag in art['tags']],
                "topics": [tag.replace("-", " ") for tag in art['topics']]
            } for art in all_articles]
    else:
        return print(f"Error fetching articles for {username}: {response.status_code} - {response.text}")

def save_json(data, filename):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__": # COME BACK TO THIS
    # fetch_medium_articles("machine-learning-made-simple")
    for gh_user in tqdm(GITHUB_USERS):
        try:
            # print(f"Processing GitHub user: {gh_user}")
            gh_repos = fetch_github_user_repos(gh_user, GITHUB_TOKEN)
            ml_repos = [repo for repo in gh_repos if is_ml_keyword(repo["description"]) or any(is_ml_keyword(topic) for topic in repo["topics"])]
            if len(ml_repos) != 0:
                save_json(ml_repos, f"{gh_user}_ml_repos.json")

            for repo in ml_repos:
                commits = fetch_github_repo_commits(gh_user, repo['name'], GITHUB_TOKEN)
                ml_commits = [c for c in commits if is_ml_keyword(c["commit"])["message"]]
                if len(ml_commits) != 0:
                    save_json(ml_commits, f"{gh_user}_{repo['name']}_ml_commits.json")
        except Exception as e:
            print(f"Error processing GitHub user {gh_user}: {e}")
    
    for so_user_id in tqdm(STACKOVERFLOW_USERS):
        try:
            # print(f"Processing Stack Overflow user ID: {so_user_id}")
            so_answers = fetch_stackoverflow_answers(so_user_id)
            ml_answers = [answer for answer in so_answers.get("items", []) if is_ml_keyword(answer.get("body", ""))]
            if len(ml_answers) != 0:
                save_json(ml_answers, f"{so_user_id}_ml_stack_answers.json")
        except Exception as e:
            print(f"\nError processing Stack Overflow user {so_user_id}: {e}")

    for blog_author in tqdm(BLOG_AUTHORS):
        try:
           # print(f"Fetching Medium articles for {blog_author}")
           medium_articles = fetch_medium_articles(blog_author)
           ml_articles = [art for art in medium_articles if is_ml_keyword(art["title"]) or is_ml_keyword(str(art["tags"])) or is_ml_keyword(str(art["topics"]))]
           if len(ml_articles) != 0:
               save_json(ml_articles, f"{blog_author.replace('/', '_')}_ml_articles.json")
        except Exception as e:
            print(f"Error processing blog author {blog_author}: {e}")