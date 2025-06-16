from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os, time
from tqdm import tqdm
from dotenv import load_dotenv
import json
load_dotenv()

edge_driver_path = os.getenv("EDGE_DRIVER_PATH")  # Default to 'msedgedriver.exe' if not set
service = Service(edge_driver_path)
options = EdgeOptions()
driver = webdriver.Edge(service=service, options=options)

ML_KEYWORDS = [
    "machine learning", "deep learning", "artificial intelligence",
    "neural networks", "computer vision", "natural language processing",
    "reinforcement learning", "data science", "big data", "AI ethics", "transformers", "transformer", 
    "GPT", "BERT", "PyTorch", "TensorFlow", "Keras", "scikit-learn",
    "huggingface", "gradient descent", "backpropagation", "convolutional neural networks",
    "recurrent neural networks", "LSTM", "GANs", "autoencoders", "unsupervised learning"]

pages = ["https://github.com/", "https://medium.com/"]

def medium_users() -> set:
    medium_set = set()
    driver.get(pages[1])
    time.sleep(10)
    sign_in_link = driver.find_element(By.LINK_TEXT, "Sign in")
    sign_in_link.click()
    wait = WebDriverWait(driver, 30)
    email_click = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.cr.b.ej.ek.cu.hl.gq.dn.hm.hn.dc.dd.di.ho.hp.hq.hr.hs.dj.v.dk.dl.dm")))
    email_click.click()
    email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.io.bz.bx.cb.ip.iq.ir.is.it.iu.n")))
    email_input.send_keys(os.getenv("MEDIUM_EMAIL"))
    time.sleep(30)
    for keyword in tqdm(ML_KEYWORDS):
        time.sleep(15)
        try:
            driver.get(f"https://medium.com/search/users?q={keyword.replace(' ', '+')}")
            time.sleep(5)
            user_names = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='search-user-preview']")
            for user in user_names:
                link = user.find_element(By.CSS_SELECTOR, "a").get_attribute("href")[8:]
                if link.find("medium") == 0:
                    medium_set.add(link[link.find("/") + 2:link.find("?")])
                else:
                    medium_set.add(link[0:link.find(".")])
            driver.get(pages[1])
            print(medium_set)
        except TimeoutException:
            print("Failed to load GitHub page within the timeout period.")
            driver.get(pages[1])
        except Exception as e:
            print(f"An error occurred: {e}")
    return medium_set

def github_users() -> set:
    github_people = set()
    for keyword in tqdm(ML_KEYWORDS):
        try:
            driver.get(pages[0] + f"search?q={keyword.replace(' ', '+')}&type=users&s=followers&o=desc")
            time.sleep(10)
            usernames = driver.find_elements(By.CSS_SELECTOR, "div.Box-sc-g0xbh4-0.MHoGG.search-title")
            for user in usernames:
                name = user.find_elements(By.TAG_NAME, "a")
                github_people.add(name[1].find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME, "span").text)
        except Exception as e:
            print(f"Error occured: {e}")
    return github_people

def web_scraper():
    try:
        github_people = github_users()
        print(github_people)
        medium_people = medium_users()
        print(medium_people)
        with open("ml_expert_sources.json", "r", encoding="utf-8") as f:
            expert_sources = json.load(f)
            expert_sources["medium_authors"].extend(medium_people)
            expert_sources["github_users"].extend(github_people)
            json.dump(expert_sources, f, indent=2)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        github_people = github_users()
        print(github_people)
        medium_people = medium_users()
        print(medium_people)
        with open("ml_expert_sources.json", "r", encoding="utf-8") as f:
            expert_sources = json.load(f)
            expert_sources["medium_authors"].extend(medium_people)
            expert_sources["github_users"].extend(github_people)
            json.dump(expert_sources, f, indent=2)
    except Exception as e:
        print(f"An error occurred: {e}")