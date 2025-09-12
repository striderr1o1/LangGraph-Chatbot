from langchain.text_splitter import RecursiveCharacterTextSplitter
import PyPDF2
import streamlit as st
from langchain_community.embeddings import OllamaEmbeddings
import os
import chromadb
from dotenv import load_dotenv


load_dotenv()

def readPDF(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text+= page.extract_text()
    return text


    
    

def SplitText(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size = 600, chunk_overlap = 100)
    splitted_text = splitter.split_text(text)
    return splitted_text

def createEmbeddings(chunks):
    response = OllamaEmbeddings(model=os.environ.get("OLLAMA_EMBEDDING_MODEL"), base_url="http://localhost:11434").embed_documents(chunks)
    return response

def storeInChromaDB(embeddings, texts):
    try:
        client = chromadb.PersistentClient(path="chromaDB")
        collection = client.get_or_create_collection(name="rag-docs")
        existing_count = collection.count()
        collection.add(
        embeddings=embeddings,
        documents=texts,
        ids= [str(i + existing_count + 1) for i in range(len(texts))]
        )
        return "Successfully ingested"
    except Exception as e:
        return f"Exception: {e}"

def check_database_contents():
    client = chromadb.PersistentClient(path="chromaDB")
    collection = client.get_or_create_collection(name="rag-docs")
    
    print(f"Total documents: {collection.count()}")
    
    # Get all documents
    all_docs = collection.get()
    
    for i, (doc_id, doc_text) in enumerate(zip(all_docs['ids'], all_docs['documents'])):
        print(f"ID: {doc_id}")
        print(f"Content preview: {doc_text[:300]}...")
        print("---")
        # if i >= 5:  # Limit output
        #     break

