import os
from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import initialize_agent, AgentType
from tools import search_documents, get_recent_documents, summarize_document


model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
tools = [search_documents, get_recent_documents, summarize_document]
model_with_tools = model.bind_tools(tools)


agent = initialize_agent(
    tools=tools,
    llm=model,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, # instructs agent to pick tools
    verbose=True
)

if __name__ == "__main__":
    query = "Show me the  recent climate changes notices."
    response = agent.run(query)
    print("🤖 Agent:", response)
