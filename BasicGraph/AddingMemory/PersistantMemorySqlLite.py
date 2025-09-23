from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated
from langchain_core.tools import tool 
from dotenv import load_dotenv
from langchain.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchRun

from pprint import pprint
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3



sqlite3_connect=sqlite3.connect("PersistantMemory.sqlite",check_same_thread=False)

checkpoint=SqliteSaver(sqlite3_connect) #* this is basic intialization for Memory | Short term memory


load_dotenv()
model=ChatGroq(model="llama-3.1-8b-instant")




class Object(TypedDict):
    messages:Annotated[list,add_messages]


graph_Builder=StateGraph(Object)

LLMNode="llmnode"



def LLm(state:Object):
    return {
        "messages":[model.invoke(state["messages"])]
    }



graph_Builder.add_node(LLMNode,LLm)
graph_Builder.add_edge(START,LLMNode)
graph_Builder.add_edge(LLMNode,END)



graph=graph_Builder.compile(checkpointer=checkpoint)#*We are pass memory to our GRAPH 

while (True):
    query=input("USER:")
    if(query=="exit"):
        break
    response=graph.invoke({
        "messages":query
    },
    {"configurable": {"thread_id": "user123"}}#*what ever the context i give it stored to this thread
    )
    print("AI:"+response['messages'][-1].content)
    


