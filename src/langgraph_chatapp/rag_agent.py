from langchain_community.embeddings import OllamaEmbeddings
import os
from langgraph.graph import add_messages
from dotenv import load_dotenv
import chromadb
from groq import Groq
import streamlit as st

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
    
    with open("context.txt", "r") as file:
        user_instructions = file.read()
    
    
    context = st.session_state["context"]   
    query = f"previous chats: {context}... retrieved results: {results}...User Query: {state['messages'][-1].content}"   
    # query = f" retrieved results: {results}...User Query: {state['messages'][-1].content}"
    answer = client.chat.completions.create(
        model=os.environ.get('CHAT_GROQ_MODEL'),
        messages=[
            {"role": "system", "content": f"""You are an Ai agent that adapts to user instructions.
                                            You are passed previous chats, retrieved results, and the user query.
                                            You should remember the context of the chat, but your main FOCUS should
                                            be answering user queries from the retrieved results. Do not mention previous
                                            chats unless told so, but keep them in your context. BUT FOCUS ON RETRIEVED RESULTS.
                                            Here are the INSTRUCTIONS that you need to follow: {user_instructions}"""
            },
            {
                "role":"user", "content":query
            }
        ]
    )
    
    state["answer"]=answer.choices[0].message.content
    

    return state