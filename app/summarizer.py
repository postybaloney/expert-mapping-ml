import json
from pathlib import Path
from dotenv import load_dotenv
import os
from tqdm import tqdm
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from langchain.output_parsers import ResponseSchema, StructuredOutputParser, PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
load_dotenv()

DATA_DIR = Path("data/raw")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Set your OpenAI API key as an environment variable

class Contribution(BaseModel):
    project: str = Field(..., description="Name of the project or contribution")
    description: Optional[str] = Field(..., description="Brief description of the contribution")
    url: Optional[str] = Field(..., description="Link to the project or contribution")

class ExpertProfile(BaseModel):
    expertise: str = Field(..., description="Expertise in machine learning")
    top_skills: Optional[List[str]] = Field(..., description="Top skills in machine learning")
    notable_contributions: Optional[List[Contribution]] = Field(..., description="Notable contributions to machine learning")
    references: Optional[List[dict]] = Field(..., description="Links to any references or publications")
    other_information: Optional[dict] = Field(..., description="Any other relevant information about the expert")

llm = ChatOpenAI(temperature=0, model="gpt-4", openai_api_key=OPENAI_API_KEY)

profile_schema = ResponseSchema(
    name="expert_profile",
    description="Structured summary of the expert's machine learning experience, top skills, and notable contributions."
)

output_parser = PydanticOutputParser(pydantic_object=ExpertProfile)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in summarizing machine learning professionals' profiles."),
    ("human", "Please summarize the following profile:\n{raw_input}"),
    ("human", "Provide a structured JSON summary with the following fields: "
          "expertise, top_skills, notable_contributions, links to any references, and any other relevant information."),
    ("human", "Follow this format: \n {format_instructions}")
])

def summarize_expert(username: str):
    files = list(DATA_DIR.glob(f"{username}*.json"))
    raw_blobs = []

    for f in files:
        with open(f, "r", encoding="utf-8") as infile:
            content = json.load(infile)
            raw_blobs.append(json.dumps(content)[:4500])

    combined_text = "\n\n".join(raw_blobs)

    prompt = prompt_template.format_messages(raw_input=combined_text, format_instructions=output_parser.get_format_instructions())
    response = llm.invoke(prompt)
    try:
        parsed_response = output_parser.parse(response.content)
    except Exception as e:
        print(f"Parsing failed: {response.content}")
        raise e
    
    with open(f"data/raw/{username}_profile.json", "w", encoding="utf-8") as outfile:
        json.dump(parsed_response.model_dump_json(), outfile, indent=2)

    print(f"Profile for {username} summarized and saved to data/raw/{username}_profile.json")


if __name__ == "__main__":
    usernames = ["karpathy", "lucidrains", "3494126"]
    for user in tqdm(usernames):
        summarize_expert(user)