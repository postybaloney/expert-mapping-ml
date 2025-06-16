## Setup

1. Install Dependencies
```bash
pip install -r requirements.txt
```

2. Fill Out the .env file
```txt
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
RAPIDAPI_KEY=...
RAPIDAPI_HOST=medium2.p.rapidapi.com
MEDIUM_EMAIL=...@*.com
```

3. Create an ml_expert_sources.json file
```bash
touch ml_expert_sources.json
```

Use this formatting:
```txt
{
  "github_users": [...],
  "stackoverflow_users": [...],
  "medium_authors": [...],
  "additional-data-source": [...]
}
```

4. Run scrapper.py
```python
python scrapper.py
```

5. Run collector.py
```python
python collector.py
```

6. Run summarizer.py
```python
python summarizer.py
```

7. Run graph.py
```python
python graph.py
```

8. Navigate to the app folder and then run app.py
```bash
cd app
```
```python
uvicorn api:app --reload
```

The server is now active!

9. Navigate to the localhost url given and add the suffix /docs
```
https://localhost:8000/docs # as an example
```
You can now input any query for the ones delineated in app.py

Alternatively, you can just run the main.py file
```python
python main.py
```

10. Select Examples

10.1. "/search"
Query:
```curl
curl -X 'POST' \
  'http://127.0.0.1:8000/search?query=transformer&page=1&page_size=10&sort_by=project_count' \
  -H 'accept: application/json' \
  -d ''
  ```
  Response:
  ```txt
  {
  "query": "transformer",
  "page": 1,
  "page_size": 10,
  "results": [
    {
      "username": "lucidrains",
      "score": 0.6759586334228516,
      "matched_skills": [
        "<b>Transformer</b>s"
      ],
      "matched_projects": [
        {
          "name": "Adjacent Attention Network",
          "description": "",
          "url": "https://github.com/lucidrains/adjacent-attention-network",
          "proj_score": 0
        },
        {
          "name": "Alphafold3 PyTorch",
          "description": "",
          "url": "https://github.com/lucidrains/alphafold3-pytorch",
          "proj_score": 0
        },
        {
          "name": "Audiolm PyTorch",
          "description": "",
          "url": "https://github.com/lucidrains/audiolm-pytorch",
          "proj_score": 0
        },
        {
          "name": "Block Recurrent <b>Transformer</b> PyTorch",
          "description": "",
          "url": "https://github.com/lucidrains/block-recurrent-transformer-pytorch",
          "proj_score": 0
        }
      ]
    },
    {
      "username": "karpathy",
      "score": 0.5715205669403076,
      "matched_skills": [],
      "matched_projects": [
        {
          "name": "minGPT",
          "description": "",
          "url": "https://github.com/karpathy/minGPT",
          "proj_score": 0
        },
        {
          "name": "char-rnn",
          "description": "",
          "url": "https://github.com/karpathy/char-rnn",
          "proj_score": 0
        }
      ]
    },
    {
      "username": "3494126",
      "score": 0.5364158153533936,
      "matched_skills": [],
      "matched_projects": [
        {
          "name": "StackOverflow Contributions",
          "description": "",
          "url": "https://stackoverflow.com/users/3494126/ufos",
          "proj_score": 0
        }
      ]
    }
  ]
}
```

10.2. "/experts/by-skill/{skill_name}"
Query: "experts/by-skill/PyTorch"
Response: 
```txt
{
    "skill":"PyTorch","experts":[
        {
            "username":"lucidrains",
            "expertise":"Machine Learning, Deep Learning, Neural Networks"
        }, 
        {
            "username":"benjybo7",
            "expertise":"Machine Learning and Data Science"
        }
    ]
}
```

10.3. "/experts/{username}"
Query: "/experts/bigdataturkey"
Response: 
```txt
{
    "username":"bigdataturkey",
    "expertise":"Big Data and Machine Learning",
    "top_skills":[
        "Big Data", 
        "Data Science", 
        "Artificial Intelligence", 
        "Machine Learning",
        "Data Visualization"
    ],
    "notable_contributions":[
    {
      "project": "Big Data Turkey Medium Sayfas\u0131nda Nas\u0131l Yazar Olunur",
      "description": "A guide on how to become a writer for Big Data Turkey on Medium",
      "url": "https://medium.com/bigdatatr/big-data-turkey-medium-sayfas%C4%B1nda-nas%C4%B1l-yazar-olunur-7f8e57572bd3"
    },
    {
      "project": "Big Data-5V",
      "description": "An article discussing the 5Vs of Big Data",
      "url": "https://medium.com/@bigdataturkey/big-data-5v-2299c115c077"
    },
    {
      "project": "Hayat\u0131m\u0131zdaki Algoritmalar",
      "description": "An article discussing the algorithms in our lives",
      "url": "https://medium.com/bigdatatr/hayat%C4%B1m%C4%B1zdaki-algoritmalar-ee423e85edfa"
    },
    {
      "project": "Gelece\u011fe Y\u00f6n Verecek Teknolojiler/Big Data",
      "description": "An article discussing the technologies that will shape the future, focusing on Big Data",
      "url": "https://medium.com/bigdatatr/gelece%C4%9Fe-y%C3%B6n-verecek-teknolojiler-big-data-796296d32291"
    },
    {
      "project": "Big Data (B\u00fcy\u00fck Veri) Nedir?",
      "description": "An article explaining what Big Data is",
      "url": "https://medium.com/dusunenbeyinler/big-data-b%C3%BCy%C3%BCk-veri-analizi-d53d8f8ab52b"
    }
  ]
}
```