from langgraph.graph import StateGraph, MessagesState, START, END, add_messages
from typing import TypedDict, Annotated
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model=os.environ.get("CHAT_GROQ_MODEL"),
)

def database_agent(query):
    """database agent"""
def knowledge_base_agent(query):
    """RAG agent"""

model_w_tools = llm.bind_functions([database_agent, knowledge_base_agent])

class State(TypedDict):
    messages: Annotated[list, add_messages]
    decision: str

graph_builder = StateGraph(State)

def AskAgent1(state: State) -> State:
    query = input("Ask Agent: ")
    state["messages"].append({"role": "user", "content": query})
    response = model_w_tools.invoke(query)
    clean_response = response.additional_kwargs['tool_calls'][-1]["function"]['name']
    if clean_response == "database_agent" or clean_response == "knowledge_base_agent":
        print(clean_response + " called")#just to check
        state["decision"] = clean_response
        return {
        "Tool": clean_response
        }
    # return state


graph_builder = StateGraph(State)

graph_builder.add_node("AskAgent1", AskAgent1)

graph_builder.add_edge(START, "AskAgent1")
graph_builder.add_edge("AskAgent1", END)

graph = graph_builder.compile()

inputs = {
    "messages": [
        {"role": "system", "content": "call the respective function based on the user query"}
    ]
}
res = graph.invoke(inputs)
print(res)