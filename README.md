# Customer Support Agentic Workflow

This application is a basic implementation of Agentic Ai. It is powered by langgraph, groq, streamlit, sqlite3. Made in Python programming language. It is an agentic chatbot that does the following tasks based on user query, though only one task per query:

- searches the knowledge base and answers user query according to relevant docs in the vector database.
- searches the sqlite database and displays the results (not in table form though)

You can also ingest your own PDFs (other formats not supported).

## Technologies used:

- langGraph
- Groq LLMs and its API
- ChromaDB
- sqlite3
- streamlit

details can be found in the requirements file.

## How to get started?

- clone the repo. App is made using uv package manager.
- install requirements
- install ollama on your system and an embedding model
- set api keys and models in .env
```
GROQ_API_KEY = ""
CHAT_GROQ_MODEL="llama-3.3-70b-versatile"
OLLAMA_EMBEDDING_MODEL="mxbai-embed-large:latest"
```
- run streamlit app.

Note: There is a high chance that you may get errors while installing because of this inconsistent readme file. In such a case, email me at mnipk1243@gmail.com.

## Workflow:
                     Start
                      |
                      |
           Router agent(decides which tool to use)
                      |
                      |
                     / \
                    /   \
                   /     \
                  /       \
                 /         \
Knowledge base tool       database tool
            |                   |
            |                   |
             \                 /
              \               /
               \             /
                 Print Output
                      |
                      |
                     END

## Some Other Things:
- DBsetup.py: database initialization code with some sample tables
- __init__.py: required for setup

## License
 MIT (except for Israel and those complicit in the Genocide of Palestinians)

### Authored by:
- author also goes by the nickname of "Ranger".