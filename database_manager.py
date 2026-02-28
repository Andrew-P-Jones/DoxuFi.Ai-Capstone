import os
import PyPDF2
import chromadb
from google import genai
from dotenv import load_dotenv
import time

load_dotenv()

class DoxuFiDatabase:
    def __init__(self):
        # 1. Initialize Gemini Client for Embeddings
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # 2. Initialize ChromaDB (Persistent storage on your hard drive)
        # This creates a folder named 'doxufi_db' in your project
        self.chroma_client = chromadb.PersistentClient(path="./doxufi_db")
        
        # 3. Create or Get a 'Collection' (Think of it like a table in a database)
        self.collection = self.chroma_client.get_or_create_collection(name="contracts")

    def extract_and_chunk(self, pdf_path: str):
        """Extracts text from PDF and breaks it into overlapping chunks."""
        text = ""
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        # Chunking Logic
        chunks = []
        size, overlap = 1000, 200
        for i in range(0, len(text), size - overlap):
            chunks.append(text[i : i + size])
        return chunks

    def ingest_pdf(self, pdf_path: str):
        """Processes the PDF and stores it in ChromaDB with Embeddings."""
        print(f"Reading {pdf_path}...")
        chunks = self.extract_and_chunk(pdf_path)
        
        print(f"Generating embeddings for {len(chunks)} chunks...")
        
        for i, chunk in enumerate(chunks):
            # Generate Embedding using Gemini
            # Embeddings turn words into a vector: [0.12, -0.05, 0.88, ...]
            result = self.client.models.embed_content(
                model="text-embedding-004", # Optimized for search
                contents=chunk
            )
            embedding = result.embeddings[0].values
            
            # Store in ChromaDB
            self.collection.add(
                ids=[f"id_{i}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": pdf_path, "chunk_index": i}]
            )
            print(f"Chunk {i} embedded. Waiting a second...")
            time.sleep(1) # To avoid hitting rate limits
        print("Ingestion complete. Database is ready!")

    def query(self, user_question: str, n_results: int = 2):
        """Searches the database for the most relevant text chunks."""
        # 1. Embed the user's question
        query_result = self.client.models.embed_content(
            model="text-embedding-004",
            contents=user_question
        )
        query_vector = query_result.embeddings[0].values
        
        # 2. Find the closest match in ChromaDB (using Cosine Similarity)
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        return results['documents'][0] # Returns the best matching text

if __name__ == "__main__":
    db = DoxuFiDatabase()
    # Replace with your actual PDF filename
    db.ingest_pdf("personal_loan_agreement.pdf") 
    
    # Test a search
    match = db.query("What is the liability limit?")
    print(f"\nTop Search Match:\n{match}")