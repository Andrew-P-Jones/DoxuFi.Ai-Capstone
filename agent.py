import os
import json
import numpy as np
from google import genai
from google.genai import types
from pinecone import Pinecone
from lime.lime_text import LimeTextExplainer
from dotenv import load_dotenv

# Your local modules
import risk_analysis.calc_risk as risk_calc
import risk_analysis.viz as viz

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
MODEL_ID = "gemini-2.5-flash"
INDEX_NAME = "integrated-sparse-py"

# Connect to the existing index
index = pc.Index(INDEX_NAME)

# --- XAI LOGIC ---

def get_risk_probs(text_list):
    """Bridge for LIME to talk to your 60+ Red Flag dictionary."""
    results = []
    for text in text_list:
        score = risk_calc.calculate_risk_score(text)['risk_score'] / 100.0
        results.append([1 - score, score])
    return np.array(results)

# --- TOOLS ---

def fetch_legal_context(query_text: str) -> str:
    """Searches Pinecone Sparse Index for exact legal matches."""
    # Note: Using .search() for Integrated Sparse models
    results = index.search(
        project={"field_map": {"text": "chunk_text"}},
        inputs={"text": query_text},
        top_k=2
    )
    # Extract text from metadata
    matches = [res['metadata']['chunk_text'] for res in results['matches']]
    return "\n---\n".join(matches)

def run_deep_xai_analysis(snippet: str):
    """Generates LIME chart and 1-2 sentence risk explanation."""
    explainer = LimeTextExplainer(class_names=['Safe', 'Risky'])
    exp = explainer.explain_instance(snippet, get_risk_probs, num_features=5)
    
    # Trigger Matplotlib Chart
    viz.plot_explanation(exp.as_list())
    
    # 1-2 Sentence Narrative
    top_words = [word for word, score in exp.as_list() if score > 0.15]
    prompt = f"""
        Explain in 2 sentences why these words make a contract risky: {top_words}. Context: {snippet}
        Write a 1-2 sentence professional explanation for a legal client explaining why these specific words increase the contract's risk.
        """
    narrative = client.models.generate_content(model=MODEL_ID, contents=prompt)
    
    return f"XAI REPORT: {narrative.text}\nFlagged Keywords: {top_words}"

# --- THE AGENT ---

def run_docky_agent(json_input: str):
    data = json.loads(json_input)
    query = data.get("question", "")

    # Define toolset for the agent
    def analyze_risk(query_str: str):
        context = fetch_legal_context(query_str)
        return run_deep_xai_analysis(context)

    chat = client.chats.create(
        model=MODEL_ID,
        config=types.GenerateContentConfig(
            tools=[fetch_legal_context, analyze_risk],
            system_instruction=(
                "You are Docky. Use 'fetch_legal_context' for facts. "
                "Use 'analyze_risk' for safety/risk questions to trigger XAI charts."
            )
        )
    )

    print(f"--- Docky is working on: {query} ---")
    response = chat.send_message(query)
    print(f"\nFINAL RESPONSE:\n{response.text}")

if __name__ == "__main__":
    test_json = json.dumps({"question": "Explain the risk of the interest rate clauses in this loan."})
    run_docky_agent(test_json)