
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)
def generateQuery(state):
    query = state["query"]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": """You are an SQL query generator based on analyzing the user query"""
            },
            {
                "role":"user", "content":f"""Here is the query: {query}...make an SQL query based on user requirements."""
            }
        ]
    )
    llm1Query = response.choices[0].message.content
    
    finalResponse = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": """You are an SQL query analyzer. You get the SQL query and you look verify if its right. If its wrong, you correct it without delivering any other talk other than the query."""
            },
            {
                "role":"user", "content":f"""Here is the query: {query}...make an SQL query based on user requirements."""
            }
        ]
    )

