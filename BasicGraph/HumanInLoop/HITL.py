from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langchain_community.tools.tavily_search.tool import TavilySearchResults  # Latest import
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv

load_dotenv()

# Tool setup
search_tool = DuckDuckGoSearchRun()
tools = [search_tool]

# Memory
memory = MemorySaver()

# Model with tools
model = ChatGroq(model="llama-3.1-8b-instant")
llm_with_tool = model.bind_tools(tools)

# State type
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Graph builder
Builder = StateGraph(State)

# LLM Node logic
def llm_node(state: State) -> State:
    response = llm_with_tool.invoke(state["messages"])
    return {"messages": response}

# Add nodes - all lowercase for consistency
Builder.add_node("llmnode", llm_node)
Builder.add_node("tools", ToolNode(tools))

# Edges
Builder.add_edge(START, "llmnode")
Builder.add_conditional_edges("llmnode", tools_condition)
Builder.add_edge("tools", "llmnode")
Builder.add_edge("llmnode", END)

# Compile graph with interrupt before tools
graph = Builder.compile(
    checkpointer=memory,
    interrupt_before=["tools"]
)

# User query
query = "What is today's latest news in Telangana?"
state = {"messages": [{"role": "user", "content": query}]}
config = {"configurable": {"thread_id": "user123"}}

# Single invoke
response = graph.invoke(state, config)
print("Final Response:", response)

# Streaming output
import pprint
pp = pprint.PrettyPrinter(indent=2)

print("\nStreaming Output:")
for m in graph.stream(state, config, stream_mode="values"):
    pp.pprint(m)
