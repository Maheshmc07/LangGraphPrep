from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated
from langchain_core.tools import tool 
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from pprint import pprint
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
load_dotenv()

model=ChatGroq(model="llama-3.1-8b-instant")

memory=MemorySaver()



class State(TypedDict):
    Topic:str
    Genearted_Post:Annotated[list,add_messages]
    Humaanfeedback:Annotated[list,add_messages]


builder=StateGraph(State)


config={
    "configurable":{
        "thread_id":"user26"
    }
}



LLMNODE="llmnode"
HUMANNODE="humannode"
ENDNODE="endnode"



def LLM(state:State):
    topic=state["Topic"]
    feedback=state["Humaanfeedback"]
    prompt = f"""
    You are a professional content writer skilled in crafting engaging LinkedIn posts.

    Based on the following human feedback, generate a polished, audience-friendly LinkedIn post:
    - Feedback: "{feedback  if feedback else 'No feedback yet'}" for the topic "{topic}"

    The post should:
    ✔ Be clear and concise  
    ✔ Maintain a professional yet relatable tone  
    ✔ Reflect key insights or gratitude from the feedback  
    ✔ Avoid exaggerated marketing language  

    Begin the LinkedIn post directly. Do not add explanations or instructions.
    """
    response=model.invoke([SystemMessage("Consider your self has a professionl Linkdin Post writer"),HumanMessage(content=prompt)])
    print("-----------------&&&&&&------------------------")
    print(response.content)
    
    return {
        "Genearted_Post":[response.content],
        "Humaanfeedback":feedback
        
    }
    
    
    
    
def HumanFeedback2(state:State):
    feedback=interrupt("Do want to provide any sort of feedback if you like")
    
    if feedback=="done":
        return Command(
            goto=ENDNODE,
            update={
                "HumanFeedback":[HumanMessage(content=feedback+"finalized")]
            }
        )
        
       
    else:
         return Command(
            goto=LLMNODE,
            update={
                "Humaanfeedback":[HumanMessage(content=feedback)]
                
            }
            
        )
        
        

def endnode(state: State):
    print("Final post!")
    print("\n")
    print(state["Genearted_Post"][-1].content)

    return {
        "Topic": state["Topic"],
        "Genearted_Post": state["Genearted_Post"],
        "Humaanfeedback": state["Humaanfeedback"]
    }

        
        
        
builder.add_node(LLMNODE,LLM)
builder.add_node(HUMANNODE,HumanFeedback2)
builder.add_node(ENDNODE,endnode)



builder.set_entry_point(LLMNODE)
builder.add_edge(ENDNODE,END)
builder.add_edge(HUMANNODE,LLMNODE)
builder.add_edge(LLMNODE,HUMANNODE)
graph=builder.compile(checkpointer=memory)

initial={
    "Topic":"AI agents occuping IT industry",
    "Genearted_Post": [],
    "Humaanfeedback": []}
    



for chunk in graph.stream(initial, config=config):
    for node_id, value in chunk.items():
        #  If we reach an interrupt, continuously ask for human feedback

        if(node_id == "__interrupt__"):
            while True: 
                user_feedback = input("Provide feedback (or type 'done' when finished): ")

                # Resume the graph execution with the user's feedback
                
                graph.invoke(Command(resume=user_feedback), config=config)

                # Exit loop if user says done
                if user_feedback.lower() == "done":
                    break


    