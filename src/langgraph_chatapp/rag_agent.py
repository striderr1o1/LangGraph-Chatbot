from langchain_community.embeddings import OllamaEmbeddings
import os
from langgraph.graph import add_messages
from dotenv import load_dotenv
import chromadb
from groq import Groq
import streamlit as st
from langgraph_chatapp.ingestion import check_database_contents
load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)
def createEmbeddings(chunks):
    response = OllamaEmbeddings(model=os.environ.get("OLLAMA_EMBEDDING_MODEL"), base_url="http://localhost:11434").embed_query(chunks)
    
    return response


def getContext(state):
    """get context from vector db"""
    query = st.session_state['messages'][-1]["content"]
    
    embeddings = createEmbeddings(query)
    print("Made embeddings")
    client_chroma = chromadb.PersistentClient("chromaDB")
    collection = client_chroma.get_or_create_collection("rag-docs")
    results = collection.query(
        query_embeddings=embeddings,
        n_results=10
    )
    # check_database_contents()
    print("fetched results from chromadb")
    state["results"]= results["documents"]
    
    return state

def PassContextToLLM(state):
    results = state["results"]
    
    with open("context.txt", "r") as file:
        user_instructions = file.read()
    
    
    context = st.session_state["context"]
    summary_llm = client.chat.completions.create(
        model=os.environ.get('CHAT_GROQ_MODEL'),
        messages=[
            {"role": "system", "content": f"""You are a chat summarizer. You will summarize chat history for another Ai to digest. If there is no context, you return an empty string."""
            },
            {
                "role":"user", "content": f"""Sumarize this chat: {context}"""
            }
        ]
    )
    summarized_context = summary_llm.choices[0].message.content
    print(summarized_context)
    last_query = st.session_state['messages'][-1]["content"]
    print(last_query)
    #can pass context
    print(results)
    query = f" summary of previous chats: {summarized_context}.... retrieved results: {results}...User Query: {last_query}"   
    # query = f" retrieved results: {results}...User Query: {state['messages'][-1].content}"
    answer = client.chat.completions.create(
        model=os.environ.get('CHAT_GROQ_MODEL'),
        messages=[
            {"role": "system", "content": f"""You are an Ai that adapts to user instructions.
                                            Here are the INSTRUCTIONS that you need to follow: {user_instructions}.
                                            Dont respond like this: 'Based on the previous chat and retrieved documents, here is ....'
                                            Respond like this: 'Here is what I know...'"""
            },
            {
                "role":"user", "content":query
            }
        ]
    )
    
    state["answer"]=answer.choices[0].message.content
    

    return state