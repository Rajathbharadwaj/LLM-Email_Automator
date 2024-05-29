from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_community.tools import DuckDuckGoSearchRun

# Add messages essentially does this with more
# robust handling
# def add_messages(left: list, right: list):
#     return left + right


class State(TypedDict):
    messages: Annotated[list, add_messages]


from langchain_core.tools import tool


# @tool
# def search(query: str):
#     """Call to surf the web."""
#     # This is a placeholder, but don't tell the LLM that...
#     return [
#         "Try again in a few seconds! Checking with the weathermen... Call be again next."
#     ]


tools = [DuckDuckGoSearchRun(name="Search")]

from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools)

from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
model = model.bind_tools(tools)

from typing import Literal


# Define the function that determines whether to continue or not
def should_continue(state: State) -> Literal["__end__", "action"]:
    messages = state["messages"]
    last_message = messages[-1]
    # If there is no function call, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"
    
# Define the function that calls the model
def call_model(state):
    messages = []
    for m in state["messages"][::-1]:
        messages.append(m)
        if len(messages) >= 5:
            if messages[-1].type != "tool":
                break
    response = model.invoke(messages[::-1])
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


from langgraph.graph import StateGraph, END

# Define a new graph
workflow = StateGraph(State)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
app = workflow.compile()


from IPython.display import Image, display

display(Image(app.get_graph(xray=True).draw_mermaid_png()))

from langchain_core.messages import HumanMessage

inputs = {
    "messages": [
        HumanMessage(
            content="what is the weather in sf? Don't give up! Keep using your tools."
        )
    ]
}
for event in app.stream(inputs, stream_mode="values"):
    # stream() yields dictionaries with output keyed by node name
    for message in event["messages"]:
        message.pretty_print()
    print("\n---\n")