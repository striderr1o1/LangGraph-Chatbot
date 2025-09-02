from langgraph.graph import StateGraph, MessagesState, START, END, add_messages
from typing import TypedDict, Annotated
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model=os.environ.get("CHAT_GROQ_MODEL")
)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    continue_chat: bool
