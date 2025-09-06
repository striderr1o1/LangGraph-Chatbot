from langchain_community.embeddings import OllamaEmbeddings
import os
from langgraph.graph import add_messages
from dotenv import load_dotenv
import chromadb
from groq import Groq
#take query
#make embeddings
#search chromadb
#get context
#send to llm
#state["knowledgeBaseResponse"] = llm response
#print by sending to next node

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

def createEmbeddings(chunks):
    response = OllamaEmbeddings(model=os.environ.get("OLLAMA_EMBEDDING_MODEL"), base_url="http://localhost:11434").embed_query(chunks)
    return response


def getContext(state):
    """get context from vector db"""
    query = state['messages'][-1]
    embeddings = createEmbeddings(query)
    print("Made embeddings")
    client = chromadb.PersistentClient("chromaDB")
    collection = client.get_or_create_collection("rag-docs")
    results = collection.query(
        query_embeddings=embeddings,
        n_results=5
    )
    print("fetched results from chromadb")
    state["results"]= results
    return state

def PassContextToLLM(state):
    results = state["results"]
    chats = state["context"]
    
    query = f" previous chats: {chats}context: {results}...User Query: {state['messages'][-1].content}"
    answer = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": """Your task is to analyze the context
                                            and answer the user query from the results. Be precise"""
            },
            {
                "role":"user", "content":query
            }
        ]
    )
    state["context"]+=f"""\n\nUser: {state["messages"][-1].content}"""
    state["answer"]=answer.choices[0].message.content
   
    return state