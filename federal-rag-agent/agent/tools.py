from langchain.agents import tool
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import pyodbc

# DB Connection
def get_db_connection():
    try:
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"  # or "." (dot)
            "DATABASE=FederalRegistry;"
            "Trusted_Connection=yes;"
        )

        conn = pyodbc.connect(conn_str)
        print("✅ DB Connected successfully!")

        return conn
    except Exception as e:
        print("❌ Error while connecting to MySQL", e)
        return None


# Tool 1: Search documents by keyword
@tool
def search_documents(keyword: str, start_date: str = None, end_date: str = None):
    """Search documents by keyword in title, abstract, or agency between dates (YYYY-MM-DD)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    SELECT document_number, title, abstract, agency_names
    FROM documents
    WHERE
    title LIKE ? OR
    abstract LIKE ? OR
    agency_names LIKE ?;
    """

    params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
    cursor.execute(sql, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    print("Result of search document tool: ", str(results))
    return str(results)

# Tool 2: Get recent documents
@tool
def get_recent_documents(days: int = 7):
    """Fetch recent N-day documents."""
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
            SELECT TOP (10) document_number, title, publication_date
            FROM documents
            WHERE publication_date >= DATEADD(DAY, -?, CAST(GETDATE() AS DATE))
            ORDER BY publication_date DESC;
        """
    cursor.execute(sql, (days,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Tool 3: Summarize by ID
@tool
def summarize_document(doc_id: str) -> str:
    """Summarize a document using its ID (document_number)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
    SELECT title, abstract FROM documents WHERE document_number=?
    """
    cursor.execute(sql, (doc_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    if not results:
        return "Document not found."
    return f"Title: {results['title']}\nAbstract: {results['abstract']}"

# Tool 4: Doing semantic search for vector DB
@tool
def semantic_search(query: str, k: int = 5):
    """Semantic search on document embeddings."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectordb = Chroma(persist_directory="./chroma_store", embedding_function=embeddings)
    docs = vectordb.similarity_search(query, k=k)
    return [{"id": d.metadata.get("id"), "title": d.page_content} for d in docs]

