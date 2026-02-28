import re
import os
from google import genai

def query_vector_db(contract_element: str) -> str:
    """
    Searches the DoxuFi vector database for specific clauses. 
    Use this when the user asks 'What does the contract say about X?'
    """
    mock_db = {
        "liability": "Section 8.2: Total liability is capped at $50,000.",
        "termination": "Section 4.1: Either party may terminate with 30 days notice.",
        "governing law": "Section 12: Governing law is the State of Delaware."
    }
    return mock_db.get(contract_element.lower(), "Clause not found.")

# Initialize a separate client or pass the existing one to the tool
def simplify_legalese(complex_text: str, client_instance) -> str:
    """
    Translates complex legal jargon into plain English using an LLM.
    """
    prompt = f"""
    You are a plain-English legal translator. 
    Take the following legal text and rewrite it so a teenager could understand it.
    Keep it concise but don't lose the original meaning.
    
    TEXT: {complex_text}
    """
    
    # We call Gemini specifically for this task
    response = client_instance.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    return response.text

def extract_entities(text_input: str) -> dict:
    """
    Extracts key metadata like Dates, Amounts, and Parties from the text.
    Use this for questions like 'Who are the parties?' or 'How much is the fee?'.
    """
    # Mock logic using regex to simulate entity extraction
    amounts = re.findall(r'\$\d+(?:,\d+)?', text_input)
    return {
        "parties": ["DoxuFi Corp", "User Client"],
        "amounts_found": amounts if amounts else "None found",
        "effective_date": "January 1, 2026"
    }

def check_missing_clauses(document_type: str) -> list:
    """
    Checks the document against a standard checklist to see what's missing.
    Use this when the user asks 'Is this a good contract?' or 'What is missing?'.
    """
    standard_checklist = ["Non-Compete", "Intellectual Property", "Indemnification", "Force Majeure"]
    # Mocking that Force Majeure is missing
    return [clause for clause in standard_checklist if clause == "Force Majeure"]

def get_xai_explanation(legal_clause: str) -> str:
    """
    Provides a risk score and explains the reasoning behind a model's classification.
    """
    return f"XAI Analysis: High Risk. The 'liability' keywords triggered a 85% confidence score for predatory terms."



# tools.py addition

def calculate_risk_score(legal_text: str) -> dict:
    """
    Analyzes text for 'Red Flag' keywords and returns a risk score.
    This fulfills the XAI (Explainable AI) requirement.
    """
    red_flags = {
        "automatic renewal": 30,
        "non-refundable": 25,
        "indemnify": 20,
        "limitation of liability": 15,
        "arbitration": 10
    }
    
    score = 0
    found_flags = []
    
    text_lower = legal_text.lower()
    for flag, weight in red_flags.items():
        if flag in text_lower:
            score += weight
            found_flags.append(flag)
            
    return {
        "risk_score": min(score, 100),
        "explanation": f"Score based on presence of: {', '.join(found_flags)}" if found_flags else "No standard red flags found.",
        "severity": "High" if score > 50 else "Medium" if score > 20 else "Low"
    }