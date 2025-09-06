from langgraph.graph import StateGraph, MessagesState, START, END, add_messages
from typing import Annotated
from typing_extensions import TypedDict
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph_chatapp.rag_agent import getContext, PassContextToLLM
import streamlit as st
load_dotenv() 

llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model=os.environ.get("CHAT_GROQ_MODEL"),
)


#state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    decision: str
    results: str
    answer: str
    context: str

#database function
def database_agent(state: State)->State:
    """"""
#knowledge base function
def knowledge_base_agent(state: State)->State:
    getContext(state)
    PassContextToLLM(state)
    return state
def print_output(state: State)->State:
    # print(state["answer"])
    st.chat_message("ai").write(state["answer"])
    state["context"]+=f"\n\nAI: {state['answer']}"
    st.session_state["messages"].append({"role": "ai", "content": state["answer"] })
    
    return state
model_w_tools = llm.bind_functions([database_agent, knowledge_base_agent])
graph_builder = StateGraph(State)

def AskAgent1(state: State) -> State:
    
    #set context, either in string or lists
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])
    if query := st.chat_input("Ask a question..."):
        state["query"] = query
        
        st.chat_message("user").write(query)
        context_w_query = f"Context: {state['context']} Query: {query}"
        state["messages"].append({"role": "user", "content": context_w_query})
        st.session_state["messages"].append({"role": "user", "content": query})
    
        response = model_w_tools.invoke(str(query))
        #if exists
        if len(response.additional_kwargs) != 0:
            clean_response = response.additional_kwargs['tool_calls'][-1]["function"]['name']
            if clean_response == "database_agent" or clean_response == "knowledge_base_agent":
                # print(clean_response + " called")#just to check
                state["decision"] = clean_response
                return state
            
        else:#else return a default decision
            state["decision"] = "default"
            return state
    else:
        st.stop()

def check_decision(state: State)->State:
    if state["decision"]=="database_agent":
        st.write("[x]Database Tool Called")
        return "database_agent"
    elif state["decision"]=="knowledge_base_agent":
        st.write("[x]Rag Tool Called")
        return "knowledge_base_agent"
    else:
        st.write("[x]Rag Tool Called")
        return "knowledge_base_agent"
    



def RunWorkFlow():
    
    graph_builder = StateGraph(State)
    
    graph_builder.add_node("AskAgent1", AskAgent1)
    graph_builder.add_node('database_agent', database_agent)
    graph_builder.add_node('knowledge_base_agent', knowledge_base_agent)
    graph_builder.add_node('print_output', print_output)
    
    graph_builder.add_edge(START, "AskAgent1")
    graph_builder.add_conditional_edges(
        "AskAgent1",
        check_decision,
        {
            "database_agent": "database_agent",
            "knowledge_base_agent": "knowledge_base_agent"
        }
    )
    graph_builder.add_edge("database_agent", "print_output")
    graph_builder.add_edge("knowledge_base_agent", "print_output")
    graph_builder.add_edge("print_output", END)
    
    graph = graph_builder.compile()
    
    inputs = {
    "messages": [
        {"role": "system", "content": "call the respective function based on the user query"}
    ],
    "query": "",
    "decision": "",
    "results": "",
    "answer": "",
    "context": st.session_state["context"]   # empty string to start
}
    finalstate = graph.invoke(inputs)
    st.session_state["context"] += finalstate["context"]
    print("Final: ",st.session_state["context"])