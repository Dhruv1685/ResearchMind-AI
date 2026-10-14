# ResearchMind AI

**Intelligent Research Paper Recommendation, Summarization and Research Gap Discovery**

An AI/ML-powered academic research assistant that searches literature via a local **arXiv Scientific CSV Dataset (287,000+ papers)** or the **arXiv Open API**, generates sentence-level embeddings for paper recommendations, produces structured summaries with an LLM, and synthesizes potential research gaps across multiple papers.

The dashboard is a minimalist **Next.js + shadcn/ui** interface (Geist typeface) served by a **FastAPI** backend.

---

## Problem Statement

Navigating hundreds of scientific publications during literature review is time-consuming. Traditional search engines rely purely on keyword matching, which misses semantically relevant papers that use different terminology. Reading entire papers to extract methodologies, findings and unaddressed research gaps requires significant manual effort.

---

## Project Objectives

1. **Automate Literature Retrieval:** Search 287,000+ papers locally from `dataset/arXiv_scientific_dataset.csv` or fetch live publications via the arXiv Open API.
2. **Semantic Paper Recommendation (ML):** Map paper text into 384-dimensional embeddings using **Sentence-BERT (`all-MiniLM-L6-v2`)** and rank recommendations via **Cosine Similarity**.
3. **Structured AI Summarization (GenAI):** Use **Google Gemini** to decompose paper abstracts into 7 factual, structured sections without hallucinating missing details.
4. **Potential Research Gap Discovery (GenAI):** Synthesize findings across multiple selected papers to identify themes, limitations, potential gaps and future directions.

---

## System Architecture

```text
                       USER INTERFACE
                  Next.js + shadcn/ui (Geist)
                              |
                              v
                      FastAPI REST layer
                  (server.py, port 8000)
                              |
                              v
                     Select Search Source
           +------------------+------------------+
           |                                     |
           v                                     v
  arXiv CSV Dataset                    arXiv Open API
  (287,000+ Papers)                    (Live Academic Feed)
           |                                     |
           +------------------+------------------+
                              |
                              v
                    Retrieved Research Papers
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
     [ Machine Learning ]              [ Generative AI ]
  Sentence-BERT Embeddings            Google Gemini LLM
  (all-MiniLM-L6-v2, 384D)              Paper Summarizer
             |                                 |
             v                                 v
      Cosine Similarity              7-part Structured Summary
             |                                 |
             v                                 +--------+
    Ranked Recommendations                     |
             |                                 |
             +----------------+----------------+
                              |
                              v
                    Multiple Selected Papers
                              |
                              v
                     Google Gemini LLM
                      (Gap Analyser)
                              |
                              v
                 Potential Research Gaps Report
                 + Future Research Directions
```

---

## Git Branching and Version Backup

| Branch Name | Description | Use Case |
| :--- | :--- | :--- |
| `dataset-version` | Local arXiv CSV Dataset (287k+ papers) with automatic fallback to the arXiv API. | Current primary version |
| `api-backup` | Pure API version without a local CSV dataset dependency. | Backup version |
| `main` | Core stable repository branch. | Main production branch |

```bash
git checkout api-backup      # API-only backup version
git checkout dataset-version # CSV dataset version
```

---

## Technology Stack

* **Programming Language:** Python 3.10+
* **Backend API:** FastAPI, Uvicorn
* **Frontend Dashboard:** Next.js 16, React 19, TypeScript
* **UI Components:** shadcn/ui, Tailwind CSS v4, Lucide icons
* **Typography:** Geist (sans) and Geist Mono
* **Data Processing and Search:** `pandas`, `re`, CSV dataset indexing
* **Academic Search API:** arXiv Atom/XML API
* **Machine Learning and Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`), `scikit-learn` (`cosine_similarity`), `numpy`
* **Generative AI and LLM:** Google Gemini API, `requests`, `python-dotenv`

---

## Module Breakdown

### Module 1: Research Paper Search (Dual Source)

* **Local CSV Dataset Search:** Fast keyword and relevance search over `dataset/arXiv_scientific_dataset.csv` containing **287,421 research papers** with columns: `id`, `title`, `category`, `published_date`, `authors`, `summary`.
* **arXiv Open API Search:** Live query execution against the arXiv Open Academic Repository.
* **Automatic Fallback:** Switches to live API search when the local dataset returns no results or the file is missing.

### Module 2: ML-Based Paper Recommendation

* Combines paper titles and abstracts into textual representations.
* Uses **Sentence-BERT (`all-MiniLM-L6-v2`)** to convert text into **384-dimensional dense vectors**.
* Calculates pairwise **Cosine Similarity** between a target paper and all retrieved papers.
* Displays top recommended papers with match percentage scores.

### Module 3: AI Paper Summarization

* Leverages **Google Gemini** to analyze paper title and abstract.
* Generates a structured summary containing 7 key sections: Research Problem, Objective, Methodology, Key Findings, Key Contribution, Limitations, Simple Explanation.
* Zero-hallucination prompt constraints. Missing information outputs `"Not specified in the provided abstract."`

### Module 4: AI Research Gap Identification

* Combines titles, abstracts and summaries of **2 or more selected papers**.
* Uses Gemini to synthesize cross-paper patterns and generate: Common Research Themes, Common Limitations, Potential Research Gaps, Possible Future Research Directions, Confidence and Evidence Explanation.
* **Disclaimer:** Identifies potential research gaps based on the analyzed papers; it does not claim global novelty.

---

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Dhruv1685/ResearchMind-AI.git
cd ResearchMind-AI
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Dataset Placement

Ensure the CSV dataset is located in the `dataset/` folder:

```
ResearchMind-AI/
+-- dataset/
    +-- arXiv_scientific_dataset.csv
```

Large `.csv` files are git-ignored by default; folder structure is preserved with `dataset/.gitkeep`.

### 5. Configure the API Key

1. Obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Copy `.env.example` to `.env`.
3. Add your key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## Running the Application

Start the FastAPI backend (terminal 1):

```bash
python server.py
```

Start the dashboard (terminal 2):

```bash
cd frontend
npm run dev
```

The dashboard opens at `http://localhost:3000` and talks to the API at `http://127.0.0.1:8000`.

To point the frontend at a different API host, set `NEXT_PUBLIC_API_URL` in `frontend/.env.local`.

### API Endpoints

| Method | Path | Purpose |
| :--- | :--- | :--- |
| GET | `/api/status` | Gemini key and dataset availability |
| POST | `/api/search` | Search papers by topic, limit and source |
| POST | `/api/recommend` | Sentence-BERT cosine similarity ranking |
| POST | `/api/summarize` | 7-part structured summary |
| POST | `/api/gap` | Multi-paper research gap report |

---

## AI vs ML Architecture Distinction (Viva Reference)

* **Machine Learning (Module 2):** Feature extraction via `Sentence-BERT` deep embeddings and mathematical vector operations (`Cosine Similarity`). Deterministic ranking.
* **Generative AI (Modules 3 and 4):** Text-to-text generation via `Google Gemini LLM`. Natural language synthesis, prompt engineering, zero-hallucination constraints and cross-document reasoning.

---

## Limitations and Future Scope

* **Current Limitations:** Analyzes arXiv open-access repository papers and local dataset abstracts (PDF full-text parsing not included in V1).
* **Future Scope:** PDF parsing (PyPDF2/PDFPlumber), vector database storage (ChromaDB/FAISS), Retrieval-Augmented Generation (RAG) and journal impact factor integration.
