import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_api_key():
    """
    Retrieve the Gemini API key from environment variables.
    """
    return os.environ.get("GEMINI_API_KEY", "").strip()


def format_papers_for_prompt(papers):
    """
    Formats multiple papers (titles, abstracts, and optional summaries) into a structured text context.

    Parameters:
        papers (list): List of paper dictionaries.

    Returns:
        str: Formatted context string for the LLM prompt.
    """
    context_blocks = []

    for idx, paper in enumerate(papers, start=1):
        title = paper.get("title", "No Title")
        paper_id = paper.get("paperId", "N/A")
        year = paper.get("year", "N/A")
        abstract = paper.get("abstract", "No abstract available.")
        summary = paper.get("summary", "No pre-generated summary.")

        block = (
            f"--- PAPER #{idx} ---\n"
            f"Title: {title}\n"
            f"Paper ID: {paper_id} (Year: {year})\n"
            f"Abstract: {abstract}\n"
        )
        if summary and summary != "No pre-generated summary.":
            block += f"Structured Summary: {summary}\n"

        context_blocks.append(block)

    return "\n\n".join(context_blocks)


def build_research_gap_prompt(papers_context):
    """
    Constructs a structured prompt for multi-paper research gap identification.

    Parameters:
        papers_context (str): Combined text of selected research papers.

    Returns:
        str: Formatted prompt text.
    """
    prompt = f"""You are an expert AI research analyst for the ResearchMind AI project.

Your task is to analyze the provided set of research papers (titles, abstracts, and summaries) and identify POTENTIAL research gaps and future research directions based ONLY on the provided text.

CRITICAL SAFETY & ZERO-HALLUCINATION RULES:
1. Do NOT claim that any identified gap is globally novel or undiscovered in all literature. Frame findings prudently as "potential research gaps based on the selected papers".
2. Base all observations strictly on the provided paper texts below. Do NOT invent missing datasets, metrics, citations, or paper claims.
3. If there is insufficient evidence to determine a gap or limitation, explicitly state: "Insufficient evidence in the provided papers."
4. Clearly distinguish between explicitly stated facts/limitations and AI-inferred observations.

---
SELECTED RESEARCH PAPERS FOR ANALYSIS:
{papers_context}
---

Please generate a comprehensive, structured research gap analysis with EXACTLY the following 5 sections:

### 1. Common Research Themes
(Explain the major topics, objectives, and domain themes shared by the selected papers.)

### 2. Common Limitations
(Identify common constraints or weaknesses mentioned across the papers. Clearly distinguish between limitations explicitly stated in the papers vs AI-inferred observations.)

### 3. Potential Research Gaps
(Provide 3 to 5 potential research gaps identified from comparing these papers. For each gap, include:
  - Gap Title:
  - Explanation:
  - Supporting Papers: (Which selected papers support this observation?)
  - Gap Type: (Explicitly stated in papers OR AI-inferred from selected papers)
)

### 4. Possible Future Research Directions
(Suggest 3 to 5 practical, concrete future research directions or methodology extensions that could address the identified gaps.)

### 5. Confidence & Evidence Explanation
(Explain how strongly supported each suggested gap is based strictly on the provided paper evidence.)
"""
    return prompt


def analyze_research_gaps(papers):
    """
    Analyzes multiple research papers using Google Gemini LLM API to identify potential research gaps.

    Parameters:
        papers (list): List of paper dictionaries.

    Returns:
        str: Generated research gap analysis report.
    """
    if not papers:
        return "[!] Cannot perform analysis: No papers provided."

    if len(papers) < 2:
        return "[!] Research gap analysis requires at least 2 papers to compare and identify patterns."

    # 1. Check API Key
    api_key = get_api_key()
    if not api_key:
        return (
            "\n[!] GEMINI_API_KEY environment variable is not set.\n"
            "[!] Please set your GEMINI_API_KEY in your .env file."
        )

    # 2. Format context and prompt
    papers_context = format_papers_for_prompt(papers)
    prompt = build_research_gap_prompt(papers_context)

    # Active Gemini API model endpoints in order of priority
    models_to_try = [
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-3.8-flash",
        "gemini-2.5-pro"
    ]

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2  # Low temperature for factual, analytical output
        }
    }

    print(f"\n[+] Analyzing potential research gaps across {len(papers)} selected papers using Gemini LLM...")

    last_error = ""

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=25)

            if response.status_code == 404:
                last_error = f"Model '{model_name}' not found"
                continue
            elif response.status_code == 503:
                last_error = f"Model '{model_name}' high demand (503)"
                continue
            elif response.status_code == 400:
                return f"[!] API Error (HTTP 400): {response.text}"

            response.raise_for_status()

            result = response.json()

            candidates = result.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "No gap analysis text generated.")

            return "[!] Failed to parse gap analysis text from API response."

        except requests.exceptions.ConnectionError:
            return "[!] Network Error: Unable to connect to the internet to reach Gemini API."
        except requests.exceptions.Timeout:
            return "[!] Timeout Error: Gemini LLM API took too long to respond."
        except requests.exceptions.HTTPError as http_err:
            last_error = f"HTTP Error ({response.status_code}): {http_err}"
            continue
        except Exception as e:
            return f"[!] Unexpected Error during research gap analysis: {str(e)}"

    return f"[!] API Error: Could not reach Gemini model endpoint ({last_error}). Please check your GEMINI_API_KEY."
