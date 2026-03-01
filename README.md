# DoxuFi.Ai-Capstone
Creating an agentic RAG tool that ingests legal documents from PDFs or .docx and creates an embedded vectorized database to use for risk analysis. Will use LIME for XAI feataures and LLM API keys for chat functionality.

Libraries and things that will be used:

* LIME for XAI (SHAP would be to computationally intensive for the size of the vectors used)
* PyPDF2 for document ingestion
* Pinecone DB with sparse indexes to do key-word searches. pinecone-sparse-english-v0 is the embedding model used which captures context of words and not just the word frequency.
