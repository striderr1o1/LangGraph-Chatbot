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


#state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    decision: str
#database function
def database_agent(query):
    """database agent"""
    print("Hi, its a hardcoded database indicator message")
#knowledge base function
def knowledge_base_agent(query):
    """RAG agent"""
    print("Hi, its a hardcoded knowledgebase indicator message")

model_w_tools = llm.bind_functions([database_agent, knowledge_base_agent])
graph_builder = StateGraph(State)

def AskAgent1(state: State) -> State:
    #query
    query = input("Ask Agent: ")
    #add to state
    state["messages"].append({"role": "user", "content": query})
    #get function call from llm
    response = model_w_tools.invoke(query)
    #if exists
    if len(response.additional_kwargs) != 0:
        clean_response = response.additional_kwargs['tool_calls'][-1]["function"]['name']
        if clean_response == "database_agent" or clean_response == "knowledge_base_agent":
            print(clean_response + " called")#just to check
            state["decision"] = clean_response
            return state
        else:
            return state
    else:#else return a default decision
        state["decision"] = "default"
        return state

def check_decision(state: State)->State:
    if state["decision"]=="database_agent":
        return "database_agent"
    elif state["decision"]=="knowledge_base_agent":
        return "knowledge_base_agent"
    else:
        return "knowledge_base_agent"
    

graph_builder = StateGraph(State)

graph_builder.add_node("AskAgent1", AskAgent1)
graph_builder.add_node('database_agent', database_agent)
graph_builder.add_node('knowledge_base_agent', knowledge_base_agent)

graph_builder.add_edge(START, "AskAgent1")
graph_builder.add_conditional_edges(
    "AskAgent1",
    check_decision,
    {
        "database_agent": "database_agent",
        "knowledge_base_agent": "knowledge_base_agent"
    }
)
graph_builder.add_edge("database_agent", END)
graph_builder.add_edge("knowledge_base_agent", END)

graph = graph_builder.compile()

inputs = {
    "messages": [
        {"role": "system", "content": "call the respective function based on the user query"}
    ]
}
res = graph.invoke(inputs)
print(res)