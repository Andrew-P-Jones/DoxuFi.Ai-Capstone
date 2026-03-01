import os
import PyPDF2
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = "integrated-sparse-py"

def setup_index():
    """Ensures the sparse index exists with integrated embedding."""
    if not pc.has_index(INDEX_NAME):
        print(f"Creating Pinecone Sparse Index: {INDEX_NAME}...")
        pc.create_index_for_model(
            name=INDEX_NAME,
            cloud="aws",
            region="us-east-1",
            embed={
                "model": "pinecone-sparse-english-v0",
                "field_map": {"text": "chunk_text"} # Maps metadata field to embedding
            }
        )
    return pc.Index(INDEX_NAME)

def extract_and_chunk(pdf_path, chunk_size=512, overlap=96):
    """Reads PDF and returns overlapping text chunks."""
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i : i + chunk_size])
    return chunks

def ingest_document(pdf_path):
    index = setup_index()
    chunks = extract_and_chunk(pdf_path)
    
    print(f"Uploading {len(chunks)} chunks to Pinecone...")
    
    vectors = []
    for i, chunk in enumerate(chunks):
        # We upload the text in metadata so the integrated model can see it
        vectors.append({
            "id": f"vec_{i}",
            "metadata": {"chunk_text": chunk}
        })
    
    # Upsert to Pinecone
    index.upsert(vectors=vectors, namespace="contracts")
    print("Ingestion Complete!")

if __name__ == "__main__":
    ingest_document("personal_loan_agreement.pdf")