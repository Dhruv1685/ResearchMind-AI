# ResearchMind AI 🔬

**Intelligent Research Paper Recommendation, Summarization & Research Gap Discovery**

An AI/ML-powered academic research assistant designed to search academic literature, generate sentence-level embeddings for paper recommendations, produce structured summaries using LLMs, and synthesize potential research gaps across multiple papers.

---

## 📌 Problem Statement
Navigating hundreds of scientific publications during literature review is time-consuming and challenging for researchers. Traditional search engines rely purely on keyword matching, which misses semantically relevant papers using different terminology. Furthermore, manually reading entire papers to extract core methodologies, findings, and unaddressed research gaps requires significant effort.

---

## 🎯 Project Objectives
1. **Automate Literature Retrieval:** Fetch research paper titles, authors, publication years, abstracts, and URLs via open academic APIs.
2. **Semantic Paper Recommendation (ML):** Map paper text into continuous 384-dimensional vector embeddings using **Sentence-BERT (`all-MiniLM-L6-v2`)** and rank recommendations via **Cosine Similarity**.
3. **Structured AI Summarization (GenAI):** Use **Google Gemini Large Language Model (LLM)** to decompose complex paper abstracts into 7 factual, structured sections without hallucinating missing details.
4. **Potential Research Gap Discovery (GenAI):** Synthesize findings across multiple selected papers to identify common themes, limitations, potential research gaps, and future research directions.

---

## 🧠 System Architecture

```text
                                 USER INTERFACE
                                (Streamlit Web App)
                                         │
                                         ▼
                               Enter Research Topic
                                         │
                                         ▼
                            arXiv Academic Repository API
                                         │
                                         ▼
                               Retrieved Research Papers
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  │                                             │
                  ▼                                             ▼
       [ Machine Learning ]                                [ Generative AI ]
   Sentence-BERT Embeddings                              Google Gemini LLM
    (`all-MiniLM-L6-v2` 384D)                             Paper Summarizer
                  │                                             │
                  ▼                                             ▼
          Cosine Similarity                            7-Part Structured Summary
                  │                                             │
                  ▼                                             └────────┬────────┘
          Ranked Recommendations                                         │
                  │                                                      │
                  └──────────────────────┬───────────────────────────────┘
                                         │
                                         ▼
                              Multiple Selected Papers
                                         │
                                         ▼
                              Google Gemini LLM (Gap Analyser)
                                         │
                                         ▼
                         Potential Research Gaps Report
                         + Future Research Directions
```

---

## 🛠️ Technology Stack
* **Programming Language:** Python 3.10+
* **Frontend Web UI:** Streamlit
* **Academic Search API:** arXiv Atom/XML API
* **Machine Learning & Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`), `scikit-learn` (`cosine_similarity`), `numpy`
* **Generative AI & LLM:** Google Gemini API (`gemini-3.5-flash`), `requests`, `python-dotenv`

---

## 🧩 Module Breakdown

### Module 1: Research Paper Search
* Queries the **arXiv Academic Repository API** for a user-specified topic.
* Retrieves paper titles, authors, publication years, URLs, arXiv IDs, and abstracts.
* Handles network timeouts and missing metadata gracefully.

### Module 2: ML-Based Paper Recommendation
* Combines paper titles and abstracts into textual representations.
* Uses **Sentence-BERT (`all-MiniLM-L6-v2`)** to convert text into **384-dimensional dense vectors**.
* Calculates pairwise **Cosine Similarity** between a target paper and all retrieved papers.
* Ranks and displays top recommended similar papers with match percentage scores.

### Module 3: AI Paper Summarization
* Leverages **Google Gemini LLM** to analyze paper title and abstract.
* Generates a structured summary containing 7 key sections:
  1. Research Problem
  2. Objective
  3. Methodology
  4. Key Findings
  5. Key Contribution
  6. Limitations
  7. Simple Explanation
* Implements zero-hallucination prompt constraints. If information is missing from the abstract, outputs `"Not specified in the provided abstract."`

### Module 4: AI Research Gap Identification
* Combines titles, abstracts, and summaries of **2 or more selected papers**.
* Uses Gemini LLM to synthesize cross-paper patterns and generate:
  1. Common Research Themes
  2. Common Limitations (explicitly stated vs AI-inferred)
  3. Potential Research Gaps (with evidence & gap type tags)
  4. Possible Future Research Directions
  5. Confidence / Evidence Explanation
* **Disclaimer:** Identifies *potential research gaps based on the analyzed papers*; does not claim global novelty.

---

## 🚀 Installation & Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Dhruv1685/ResearchMind-AI.git
cd ResearchMind-AI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
1. Obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and insert your key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

---

## 💻 Running the Application

Launch the Streamlit web application:

```bash
streamlit run app.py
```
*(Or `python -m streamlit run app.py`)*

The application will automatically open in your default browser at `http://localhost:8501`.

---

## 📊 AI vs ML Architecture Distinction (Viva Reference)
* **Machine Learning (Module 2):** Feature extraction via `Sentence-BERT` deep embeddings and mathematical vector operations (`Cosine Similarity`). Deterministic ranking.
* **Generative AI (Modules 3 & 4):** Text-to-text generation via `Google Gemini LLM`. Natural language synthesis, prompt engineering, zero-hallucination constraints, and cross-document reasoning.

---

## ⚠️ Limitations & Future Scope
* **Current Limitations:** Analyzes arXiv open-access repository papers and relies on title + abstract metadata (PDF full-text parsing not included in V1).
* **Future Scope:** Integration of PDF parsing (PyPDF2/PDFPlumber), Vector Database storage (ChromaDB/FAISS), Retrieval-Augmented Generation (RAG), and journal impact factor integration.
