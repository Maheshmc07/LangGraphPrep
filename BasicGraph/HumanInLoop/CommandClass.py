from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated
from langchain_core.tools import tool 
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from pprint import pprint
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

# model = ChatGroq(model="llama-3.1-8b-instant")

#*This code will give you proper understanding of Command classs
#!Interupt function
#^No add edge is used only with command class functionality

#*         START
        #^   |
        #^ nodeA
        #^   |
        #^ nodeB
        #^   |
        #^ nodeC (INTERRUPT) - "D" --> nodeD --> END
        #^                 |
        #^                 +-- "E" --> nodeE --> END


class State(TypedDict):
    messages:str
    

memory=MemorySaver()
builder=StateGraph(State)

NODEa="nodea"
NODEb="nodeb"
NODEc="nodec"
NODEd="nodeD"
NODEe="nodee"


def nodeA(state:State):
    return Command(
        goto=NODEb,
        update={"messages":state["messages"]+'a'}
    )

def nodeB(state:State):
    return Command(
        goto=NODEc,
        update={"messages":state["messages"]+'b'}
    )
    
def nodeC(state:State):
    
    respons=interrupt("Where u want to go E or D")
  
    
    if(respons=='D'):
        return Command(
            goto=NODEd,
            update={"messages":state["messages"]+'c'}

        )
    else:
          return Command(
            goto=NODEe,
            update={"messages":state["messages"]+'c'}
     
        )
        
    
    
def nodeD(state:State):
    return Command(
        goto=END,
        update={"messages":state["messages"]+'d'}
    )


    
def nodeE(state:State):
    return Command(
        goto=END,
            update={"messages":state["messages"]+'e'}
    )



builder.add_node(NODEa,nodeA)
builder.add_node(NODEb,nodeB)
builder.add_node(NODEc,nodeC)
builder.add_node(NODEd,nodeD)
builder.add_node(NODEe,nodeE)

builder.set_entry_point(NODEa)

config = {"configurable": {"thread_id": "user23"}}



graph=builder.compile(checkpointer=memory)
intial={
    "messages":''
}

response=graph.invoke(intial,config=config)
print(response["__interrupt__"][0])

val=input("User:")


second_time=graph.invoke(Command(resume=val),config)
print(second_time["messages"])


