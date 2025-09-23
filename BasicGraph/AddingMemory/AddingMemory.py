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
from langgraph.checkpoint.memory import MemorySaver



checkpoint=MemorySaver()#* this is basic intialization for Memory | Short term memory


load_dotenv()
model=ChatGroq(model="llama-3.1-8b-instant")


#*TOOL 1
search_tool=DuckDuckGoSearchRun()

#*TOOL 2
@tool
def add(a:int ,b:int)->int:
    """This function helpful in add two numbers"""
    return a+b


tools=[search_tool,add]
model_with_tools=model.bind_tools(tools)



class Object(TypedDict):
    messages:Annotated[list,add_messages]


graph_Builder=StateGraph(Object)

LLMNode="llmnode"



def LLm(state:Object):
    return {
        "messages":[model_with_tools.invoke(state["messages"])]
    }



graph_Builder.add_node(LLMNode,LLm)
graph_Builder.add_node("tools",ToolNode(tools))

graph_Builder.add_edge(START,LLMNode)

graph_Builder.add_conditional_edges(LLMNode,tools_condition)

graph_Builder.add_edge("tools",LLMNode)

graph_Builder.add_edge(LLMNode,END)



graph=graph_Builder.compile(checkpointer=checkpoint)#*We are pass memory to our GRAPH 


query="Hey hii my name Mahesh Chandra and my age is 21 whish me good luck i got selected Hashedin internship,how are you?"
response=graph.invoke({
    "messages":query
},
 {"configurable": {"thread_id": "user123"}}#*what ever the context i give it stored to this thread
)


response=graph.invoke({
    "messages":"what is my name ?"
},
 {"configurable": {"thread_id": "user123"}}
)



val=graph.invoke({
     "messages":"what is the company which i got selected for and what is my age ?"
},
{"configurable": {"thread_id": "user123"}})




print(response['messages'][-1].content)
print(val['messages'][-1].content)




