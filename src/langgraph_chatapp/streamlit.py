import streamlit as st
from langgraph_chatapp.ingestion import readPDF, SplitText, createEmbeddings, storeInChromaDB
from langgraph_chatapp.main_agent import RunWorkFlow, State
# Page config
st.set_page_config(page_title="AI App", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Document Ingestion", "Database", "Chatbot"])

# Page 1: Document Ingestion
if page == "Document Ingestion":
    st.title("📄 Document Ingestion")
    uploaded_files = st.file_uploader("Upload documents", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        for file in uploaded_files:
            st.success(f"Uploaded: {file.name}")
            # TODO: process and store documents
        if st.button("Process Documents"):
            st.info("Processing... (placeholder)")
            # TODO: implement processing pipeline
            for file in uploaded_files:
                st.write("Ingesting File: ", file.name)
                text = readPDF(file)
                splittedText = SplitText(text)
                st.write("Chunks Count: ",len(splittedText))
                embeddings = []
                i = 0
                for text in splittedText:
                    embedded = createEmbeddings(text)
                    embeddings.append(embedded[0])
                    print(embedded[0])
                    i=i+1
                    st.write("count: ",i)
                status = storeInChromaDB(embeddings, splittedText)
                st.write(status)

# Page 2: Database
elif page == "Database":
    st.title("🗄️ Database")
    
    

# Page 3: Chatbot
elif page == "Chatbot":
    st.title("🤖 Chatbot")
    st.session_state["context"] = ""
    RunWorkFlow()
    
