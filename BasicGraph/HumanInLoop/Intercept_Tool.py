from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated
from langchain_core.tools import tool 
from dotenv import load_dotenv
from langchain.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from pprint import pprint
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
load_dotenv()

#*Interrupting our tool access


memory=MemorySaver()

class State(TypedDict):
    messages:Annotated[list,add_messages]
    
    
    #*TOOL 2
@tool
def add(a:int ,b:int)->int:
    """This function helpful in add two numbers"""
    return a+b

    

model=ChatGroq(model="llama-3.1-8b-instant")

search_tool=TavilySearchResults()
tools=[add]
LLmNode="llmnode"
Toolnode="toolnode"


llm_with_tools=model.bind_tools(tools)


builder=StateGraph(State)

def llm(state:State):
    return {
        "messages":llm_with_tools.invoke(state["messages"])
    }
    
def tool_router(state:State):
    lastmessages=state["messages"][-1]
    if(hasattr(lastmessages,"tool_calls")>0):
        return Toolnode
    else:
        return END
    


builder.add_node(LLmNode,llm)
builder.add_node(Toolnode,ToolNode(tools))


builder.add_conditional_edges(LLmNode,tool_router)
builder.add_edge(Toolnode,LLmNode)

builder.set_entry_point(LLmNode)


config={
    "configurable":{
        "thread_id":"user65"
    }
}


graph=builder.compile(checkpointer=memory,interrupt_before=[Toolnode])

intial={
   "messages":[HumanMessage(content="Add this Numbers 2+3")]

}

response=graph.invoke(intial,config=config)

pprint(response["messages"][-1].pretty_print())
print('Intrupted')
events =graph.stream(None,config,stream_mode="values")


for event in events:

    event["messages"][-1].pretty_print()
