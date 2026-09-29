import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


def get_api_key():
    """
    Retrieve the Gemini API key from environment variables.
    """
    return os.environ.get("GEMINI_API_KEY", "").strip()


def build_summarization_prompt(title, abstract):
    """
    Constructs a structured, zero-hallucination prompt for the LLM.

    Parameters:
        title (str): Research paper title.
        abstract (str): Research paper abstract.

    Returns:
        str: Formatted prompt text.
    """
    prompt = f"""You are an expert AI research assistant for the ResearchMind AI project.

Your task is to analyze the provided research paper title and abstract, and generate a concise, structured summary.

CRITICAL CONSTRAINTS TO PREVENT HALLUCINATION:
1. Base your summary ONLY on the information explicitly provided in the title and abstract below.
2. Do NOT invent, assume, or extrapolate facts, results, datasets, or conclusions not directly supported by the text.
3. If the abstract does not contain sufficient details for a specific section, write EXACTLY: "Not specified in the provided abstract."
4. Maintain a clear distinction between directly stated facts and analytical interpretation.

---
PAPER TITLE: {title}

PAPER ABSTRACT: {abstract}
---

Please generate a clean, structured summary with EXACTLY the following 7 sections:

### 1. Research Problem
(What specific problem or challenge does this paper address?)

### 2. Objective
(What is the main goal or objective of this research?)

### 3. Methodology
(What approach, algorithms, model, or methods did the researchers use?)

### 4. Key Findings
(What key results, discoveries, or outcomes did the researchers find?)

### 5. Key Contribution
(What is the primary contribution of this paper to the field?)

### 6. Limitations
(What limitations are mentioned or apparent from the provided text?)

### 7. Simple Explanation
(Explain the paper's core concept in 2-3 simple, beginner-friendly sentences.)
"""
    return prompt


def summarize_paper(title, abstract):
    """
    Generates a structured research paper summary using Google Gemini LLM API.

    Parameters:
        title (str): Paper title.
        abstract (str): Paper abstract.

    Returns:
        str: Generated structured summary or error message.
    """
    # 1. Handle empty or missing title/abstract
    if not title:
        title = "Untitled Paper"

    if not abstract or abstract.strip() == "No abstract available for this paper.":
        return "[!] Cannot generate summary: No abstract is available for this paper."

    # Handle overly long input by truncating abstract to ~3000 chars (~600 words)
    if len(abstract) > 3000:
        abstract = abstract[:3000] + "... [Abstract truncated for length]"

    # 2. Check for API Key
    api_key = get_api_key()

    if not api_key:
        return (
            "\n[!] GEMINI_API_KEY environment variable is not set.\n"
            "[!] How to fix:\n"
            "    1. Create a file named '.env' in your project root folder.\n"
            "    2. Add your Google Gemini API key: GEMINI_API_KEY=your_key_here\n"
            "    3. Get a free API key at: https://aistudio.google.com/app/apikey"
        )

    # 3. Build Prompt
    prompt = build_summarization_prompt(title, abstract)

    # Active Gemini API model endpoints in order of priority
    models_to_try = [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-flash-latest"
    ]

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2  # Low temperature for factual, deterministic output
        }
    }

    print("\n[+] Generating AI structured summary using Gemini LLM...")

    last_error = ""

    # Try model endpoints with automatic fallback
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 404:
                last_error = f"Model '{model_name}' not found"
                continue
            elif response.status_code == 503:
                last_error = f"Model '{model_name}' high demand (503)"
                time.sleep(2)
                continue
            elif response.status_code == 400:
                return f"[!] API Error (HTTP 400): {response.text}"

            response.raise_for_status()

            result = response.json()

            # Extract generated text from Gemini API response payload
            candidates = result.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "No summary text generated.")

            return "[!] Failed to parse summary text from API response."

        except requests.exceptions.ConnectionError:
            return "[!] Network Error: Unable to connect to the internet to reach Gemini API."
        except requests.exceptions.Timeout:
            return "[!] Timeout Error: Gemini LLM API took too long to respond."
        except requests.exceptions.HTTPError as http_err:
            last_error = f"HTTP Error ({response.status_code}): {http_err}"
            continue
        except Exception as e:
            return f"[!] Unexpected Error during summarization: {str(e)}"

    return f"[!] API Error: Could not reach Gemini model endpoint ({last_error}). Please verify your GEMINI_API_KEY."
