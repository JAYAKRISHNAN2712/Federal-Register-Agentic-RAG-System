# Federal-Register-Agentic-RAG-System

This project builds an Agentic Retrieval-Augmented Generation (RAG) system on top of the Federal Register API + MySQL + VectorDB using LangChain and LangGraph.

It allows you to:

+ 🔄 Ingest & sync Federal Register documents into MySQL + VectorDB
+ 🧠 Query using natural language (e.g., "Show me Defense Department notices from July 2025")
+ 🛠 Run an agent that decides between SQL queries, VectorDB semantic search, and summarization
+ ⚡ Uses Gemini-2.0-flash (for reasoning and summarization

## ⚙️ Tech Stack

+ Backend

  - 🐬 MySQL → stores structured metadata (title, abstract, agencies, publication date)
  - 📦 VectorDB (Chroma / Weaviate / Qdrant) → semantic embeddings of abstracts + full text
  - 🧑‍💻 LangChain → tool abstraction + agent orchestration
  - 🔀 LangGraph → stateful multi-step agent control

+ Pipeline

  - Daily sync from Federal Register API → MySQL + VectorDB embeddings
  - Experiment tracking via MLflow (TODO)
  
## 📂 Project Structure

```
federal-rag-agent/
│── ingest/              # Pipeline: fetch docs, insert into MySQL & VectorDB
│   └── ingest_federal_register.py
│── db/                  # Database schema + migrations
│   └── schema.sql
│── agent/               # Agent logic (LangChain + LangGraph)
│   ├── tools.py         # MySQL + VectorDB wrapped as LangChain tools
│   ├── agent.py         # LangChain agent executor
│   └── graph_agent.py   # LangGraph controlled agent
│── notebooks/           # Exploration / dev
│── README.md
```

## 🚀 Setup
## 1️⃣ Clone & Install
```
git clone https://github.com/<your-username>/federal-rag-agent.git
cd federal-rag-agent

pip install -r requirements.txt
```
requirements.txt : 
```
langchain
langgraph
langchain-community
mysql-connector-python
chromadb    # or weaviate-client / qdrant-client
ollama
```
## 2️⃣ Setup MySQL

```
CREATE DATABASE federal_register;
USE federal_register;

CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_number VARCHAR(50) UNIQUE,
    title TEXT,
    abstract TEXT,
    publication_date DATE,
    agency_names TEXT,
    html_url TEXT,
    pdf_url TEXT
);
```
## 3️⃣ Setup VectorDB

Example: ChromaDB (local)
```
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectordb = Chroma(persist_directory="./chroma_store", embedding_function=embeddings) 
```
Each document’s abstract + title is embedded into the store.

## 4️⃣ Run Ingestion
```
python ingest/ingest_federal_register.py
```
This pulls documents from the Federal Register API, stores metadata in MySQL, and embeddings in VectorDB.

## 5️⃣ Run Agent (LangChain)
```
response = agent.run("Show me the most recent Defense Department notices from July 2025")
print(response)
```
## 6️⃣ Run Agent (LangGraph)
```
python agent/graph_agent.py
```
LangGraph allows custom state machines → e.g.,

+ Step 1: Decide if SQL lookup or semantic search needed
+ Step 2: Call MySQL / VectorDB tool
+ Step 3: Summarize with LLM

## 🧰 Available Tools

+ search_documents(keyword, start_date, end_date) → SQL query in MySQL
+ get_recent_documents(days) → fetch latest docs
+ summarize_document(doc_id) → get abstract/title
+ semantic_search(query, k=5) → search in VectorDB

## 🛠 Next Steps

+ Including asynchronous operations
+ Add streaming answers (FastAPI + WebSocket frontend)
+ Add fine-tuned summarization model for legal texts
+ Extend ingestion pipeline for daily auto-update via cron
+ Multi-agent LangGraph (SQL agent + RAG agent + Summarizer agent)
