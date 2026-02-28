import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import your real database manager
from database_manager import DoxuFiDatabase

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-2.5-flash"

# 1. Initialize the Database
db = DoxuFiDatabase()

# --- THE TOOLS ---

def query_contract_database(query_text: str) -> str:
    """
    Searches the real contract PDF for clauses related to the user's query.
    Use this whenever you need factual information from the uploaded document.
    """
    print(f"DEBUG: Searching database for: '{query_text}'")
    
    # Call the query method from our DoxuFiDatabase class
    search_results = db.query(query_text, n_results=2)
    
    # Join the retrieved chunks into a single string for the AI to read
    context = "\n---\n".join(search_results)
    return context

def explain_simply(legal_text: str) -> str:
    """
    Simplifies complex legal text into everyday English.
    """
    prompt = f"Explain this legal clause in simple terms for a non-lawyer: {legal_text}"
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text

# --- THE AGENT LOOP ---

def run_doxufi_agent(user_json: str):
    data = json.loads(user_json)
    user_query = data.get("question", "")

    # Define the toolset for the agent
    tools_list = [query_contract_database, explain_simply]

    chat = client.chats.create(
        model=MODEL_ID,
        config=types.GenerateContentConfig(
            tools=tools_list,
            system_instruction=(
                "You are Docky, the DoxuFi AI legal assistant. You have access to a real vector database "
                "containing a legal contract. Always search the database before answering."
                "Use the provided tools to help users understand their contracts. "
                "Be professional, but explain things clearly. "
            )
        )
    )

    print(f"\n--- Docky is analyzing the document... ---")
    response = chat.send_message(user_query)
    
    print(f"\nFINAL ANSWER:\n{response.text}")

if __name__ == "__main__":
    
    test_request = json.dumps({"question": "What does this contract say about liability and explain it simply?"})
    run_doxufi_agent(test_request)
















    # # agent.py
# import os
# import json
# from google import genai
# from google.genai import types
# from dotenv import load_dotenv
# import tools 

# load_dotenv()
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# MODEL_ID = "gemini-2.5-flash"

# # Note: We use a lambda or a wrapper to pass the 'client' into the simplify tool
# def run_doxufi_agent(json_input: str):
#     # Parse the JSON string
#     try:
#         data = json.loads(json_input)
#         user_query = data.get("question", "")
#     except json.JSONDecodeError:
#         return "Error: Invalid JSON input."

#     print(f"\n--- Docky is processing: '{user_query}' ---")
    
#     # Define tools within the function to keep 'client' in scope
#     def simplify_wrapper(complex_text: str):
#         return tools.simplify_legalese(complex_text, client)

#     tools_list = [
#         tools.query_vector_db, 
#         tools.extract_entities, 
#         tools.check_missing_clauses,
#         tools.get_xai_explanation,
#         simplify_wrapper # Wrapper that has the LLM client
#     ]

#     chat = client.chats.create(
#         model=MODEL_ID,
#         config=types.GenerateContentConfig(
#             tools=tools_list,
#             system_instruction=(
#                 "You are Docky, the DoxuFi AI legal assistant. "
#                 "Use the provided tools to help users understand their contracts. "
#                 "Be professional, but explain things clearly. If a clause is missing, "
#                 "warn the user. Always use tools to get facts before answering."
#             )
#         )
#     )

#     response = chat.send_message(user_query)
#     print(f"\nDOCKY'S RESPONSE:\n{response.text}")

# if __name__ == "__main__":
#     # Simulating a JSON object coming from a frontend/API
#     mock_json_request = json.dumps({
#         "question": "What is the liability, and can you explain it simply?",
#         "user_id": "12345",
#         "document_id": "contract_001"
#     })
    
#     run_doxufi_agent(mock_json_request)


