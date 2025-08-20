import requests
import mysql.connector
import pyodbc
from mysql.connector import Error

# -------------------------
# 1. MySQL Connection Setup
# -------------------------
def get_db_connection():
    try:
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"  # or "." (dot)
            "DATABASE=FederalRegistry;"
            "Trusted_Connection=yes;"
        )
        # conn = mysql.connector.connect(
        #     host="localhost",
        #     user="your_mysql_user",     # <-- change this
        #     password="your_mysql_pass", # <-- change this
        #     database="federal_register" # <-- create this database first
        # )

        conn = pyodbc.connect(conn_str)
        print("✅ DB Connected successfully!")

        return conn
    except Error as e:
        print("❌ Error while connecting to MySQL", e)
        return None

# -------------------------
# 2. Create Table (Run once)
# -------------------------
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='documents' AND xtype='U')
        BEGIN
            CREATE TABLE documents (
                id INT IDENTITY(1,1) PRIMARY KEY,
                document_number VARCHAR(50) UNIQUE,
                title NVARCHAR(MAX),
                type NVARCHAR(100),
                abstract NVARCHAR(MAX),
                publication_date DATE,
                agency_names NVARCHAR(MAX),
                html_url NVARCHAR(MAX),
                pdf_url NVARCHAR(MAX)
            );
        END
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Table created (if not exists).")

# -------------------------
# 3. Insert Document
# -------------------------
def insert_document(doc):
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    MERGE documents AS target
    USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS source
       (document_number, title, type, abstract, publication_date, agency_names, html_url, pdf_url)
    ON target.document_number = source.document_number
    WHEN MATCHED THEN
    UPDATE SET 
        title = source.title,
        type = source.type,
        abstract = source.abstract,
        publication_date = source.publication_date,
        agency_names = source.agency_names,
        html_url = source.html_url,
        pdf_url = source.pdf_url
    WHEN NOT MATCHED THEN
        INSERT (document_number, title, type, abstract, publication_date, agency_names, html_url, pdf_url)
        VALUES (source.document_number, source.title, source.type, source.abstract, source.publication_date, source.agency_names, source.html_url, source.pdf_url);
    """

    agencies = ", ".join([a.get("name", a.get("raw_name", "")) for a in doc.get("agencies", [])])

    values = (
        doc.get("document_number"),
        doc.get("title"),
        doc.get("type"),
        doc.get("abstract"),
        doc.get("publication_date"),
        agencies,
        doc.get("html_url"),
        doc.get("pdf_url")
    )

    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()

# -------------------------
# 4. Fetch & Process API Data
# -------------------------
def fetch_documents(params):
    url = f"https://www.federalregister.gov/api/v1/documents.json"
    resp = requests.get(url, params=params)
    page = 1

    while url:
        print(f"📥 Fetching page {page}: {url}")
        resp = requests.get(url, params=params)
        data = resp.json()

        for doc in data.get("results", []):
            insert_document(doc)

        url = data.get("next_page_url")

        page += 1



    print("✅ All documents fetched and inserted.")

# -------------------------
# 5. Run the Pipeline
# -------------------------
if __name__ == "__main__":
    create_table()
    params = {"per_page":2, "conditions[term]":"climate change", "year":2025}
    fetch_documents(params)
