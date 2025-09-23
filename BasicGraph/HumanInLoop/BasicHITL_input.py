from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated
from langchain_core.tools import tool 
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from pprint import pprint
from langgraph.prebuilt import ToolNode,tools_condition

#& this is very basic only works at terminal not at WebApp
#& it completely freezes the flow of the program 
#& it handles one user  at a time



load_dotenv()
model=ChatGroq(model="llama-3.1-8b-instant")




class Object(TypedDict):
    messages:Annotated[list,add_messages]


graph_Builder=StateGraph(Object)

GENERATE="genearate"
APPROVE="approvenode"
FEEDBACK="feedbacknode"
POST='postnode'
def  make_graph():

    def genearation(obj:Object):
        return {
        "messages":[model.invoke(obj["messages"])]
        }
        
    def approve(obj:Object):
        response=obj["messages"][-1].content
        print("this is the Post genearated")
        print('/n')
        print(response)
        approv=input("Is this post ok for you (yes,no)")
        
        if approv.lower()=='yes':
            return POST
        else:
            return FEEDBACK
        
        
        
    def feedbacknode(obj:Object):
        feedback=input("what is the feedback that you want to give?")
        return{
            "messages":[HumanMessage(content=feedback)]
            
        }
        
        
        
    def post(obj:Object):
        response=obj["messages"][-1].content
        print("this is ur final Post genearated")
        print('/n')
        print(response)
        
    
        


    graph_Builder.add_node(GENERATE,genearation)
    graph_Builder.add_node(APPROVE,approve)
    graph_Builder.add_node(POST,post)
    graph_Builder.add_node(FEEDBACK,feedbacknode)



    graph_Builder.add_edge(START,GENERATE)
    graph_Builder.add_conditional_edges(GENERATE,approve)

    graph_Builder.add_edge(POST,END)
    graph_Builder.add_edge(FEEDBACK,GENERATE)


    graph=graph_Builder.compile()

    # response=graph.invoke({
    #     "messages":"Genearate a Blog post on AI is fun ,Rost Ai"
    # })


    # print(response["messages"][-1].content)
    return graph

agent=make_graph()