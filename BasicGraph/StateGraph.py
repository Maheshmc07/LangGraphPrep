from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated
from IPython.display import Image, display
from langchain.tools import tool
from langchain.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
from langchain.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode,tools_condition
load_dotenv()


#*DEFINING STRUCTURE
class State(TypedDict):
    messages:Annotated[list,add_messages]


#*TOOL 1
searchTool=TavilySearchResults(k=3)



#*TOOL 2
@tool
def add(a:int ,b:int)->int:
    """This function helpful in addinf two numbers"""
    return a+b



llm=ChatGroq( model="llama-3.1-8b-instant")



builder=StateGraph(State);

tools=[searchTool]

llm_bind=llm.bind_tools([searchTool,add])

#!LLMNode
def LLmNode(state:State):
    response=llm_bind.invoke(state["messages"])
    return {
        "messages":response
    }


builder.add_node("LLMNODE",llm_bind)
builder.add_node("ToolNode",ToolNode([searchTool,add]))



builder.add_edge(START,"LLMNODE")
builder.add_conditional_edges(
    "LLMNODE",
    tools_condition
)

builder.add_edge("ToolNode",END)


graph=builder.compile();


response=graph.invoke({"messages":"What is todays date and latest news in telangana"})
print(response.content)





