from langgraph.graph import StateGraph, MessagesState, START, END, add_messages
from typing import TypedDict, Annotated
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model=os.environ.get("CHAT_GROQ_MODEL")
)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    continue_chat: bool

graph_builder = StateGraph(State)


def user_query(state: State) -> State:
    user_input = input("Query:")
    state["messages"].append(HumanMessage(content=user_input))
    return state

def Chatbot(state: State) -> State:
    query = state["messages"]
    response = llm.invoke(query)
    state["messages"].append(AIMessage(content=response.content))
    return state

graph_builder.add_node('user-query', user_query)
graph_builder.add_node('chatbot', Chatbot)

graph_builder.add_edge(START, "user-query")
graph_builder.add_edge('user-query', 'chatbot')
graph_builder.add_edge('chatbot', END)

graph = graph_builder.compile()

inputs = {
    "messages": [
        SystemMessage(content="You are a helpful assistant that explains things clearly.")
    ]
}
for event in graph.stream(inputs):
    print(event)

result = graph.invoke(inputs)

