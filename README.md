# Federal-Register-Agentic-RAG-System

This project builds an Agentic Retrieval-Augmented Generation (RAG) system on top of the Federal Register API + MySQL + VectorDB using LangChain and LangGraph.

It allows you to:

🔄 Ingest & sync Federal Register documents into MySQL + VectorDB

🧠 Query using natural language (e.g., "Show me Defense Department notices from July 2025")

🛠 Run an agent that decides between SQL queries, VectorDB semantic search, and summarization

⚡ Use Ollama LLMs (e.g., qwen2.5, llama3) for reasoning and summarization
