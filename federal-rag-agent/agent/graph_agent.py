import os
from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Any
from tools import search_documents, semantic_search


llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
# Defining State
class AgentState(TypedDict):
    messages: List[Any]
    results: Any

# Define Graph Nodes
def decide_tool(state: AgentState):
    """LLM decides which tool to call (SQL or VectorDB)."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an AI agent with access to tools: search_documents (SQL) and semantic_search (Vector DB). Decide the best one."),
            ("human", "{query}")

        ]
    )

    chain = prompt | llm
    decision = chain.invoke({"query": state["messages"][-1].content})
    print("State:",{"messages":state["messages"] + [decision]})
    return {"messages":state["messages"] + [decision]}

def run_tool(state: AgentState):
    """Executes the tool chosen by the LLM."""
    last_msg = state["messages"][-1].content.lower()

    if "semantic" in last_msg:
        results = semantic_search.invoke({"query": state["messages"][-2].content})
    else:
        # Fallback to SQL search
        results = search_documents.invoke({"keyword": state["messages"][-2].content})

    return {"results": results, "messages":state["messages"]}

def summarize_results(state: AgentState):
    """Summarizes retrieved results for user."""
    results = state["results"]
    text = "\n".join([r.get("title", "") for r in results[:5]]) if results else "No results found."

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize results in a helpful way."),
        ("human", text)
    ])
    chain = prompt | llm
    summary = chain.invoke({})
    return {"messages": state["messages"] + [summary], "results": results}

# Build graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("decide_tool", decide_tool)
workflow.add_node("run_tool", run_tool)
workflow.add_node("summarize_results", summarize_results)

# Define edges
workflow.set_entry_point("decide_tool")
workflow.add_edge("decide_tool", "run_tool")
workflow.add_edge("run_tool", "summarize_results")
workflow.add_edge("summarize_results", END)

# Compile
app = workflow.compile()

if __name__ == "__main__":
    user_query = "Show me climate change notices from July 2025."

    state = {"messages": [HumanMessage(content=user_query)], "results": None}

    final_state = app.invoke(state)
    print("\n--- FINAL ANSWER ---")
    print(final_state["messages"][-1].content)



