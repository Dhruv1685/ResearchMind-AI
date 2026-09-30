"""
ResearchMind AI — Interactive Streamlit Web Application
Integrates Module 1 (Search), Module 2 (ML Recommendation), Module 3 (AI Summarization), & Module 4 (Research Gap Discovery)
"""

import os
import streamlit as st
from dotenv import load_dotenv

from backend.paper_search import search_papers
from backend.paper_recommender import recommend_similar_papers
from backend.paper_summarizer import summarize_paper, get_api_key
from backend.research_gap import analyze_research_gaps

# Load environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="ResearchMind AI",
    page_icon="🔬",
    layout="wide"
)

# Initialize Session State Variables
if "papers" not in st.session_state:
    st.session_state["papers"] = []
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = []
if "summaries" not in st.session_state:
    st.session_state["summaries"] = {}
if "gap_report" not in st.session_state:
    st.session_state["gap_report"] = ""
if "last_topic" not in st.session_state:
    st.session_state["last_topic"] = ""

# -------------------------------------------------------------
# APP HEADER
# -------------------------------------------------------------
st.title("🔬 ResearchMind AI")
st.markdown("##### *Intelligent Research Paper Recommendation, Summarization & Research Gap Discovery*")
st.divider()

# Sidebar Info & API Key Status
with st.sidebar:
    st.header("⚙️ System Status")
    api_key = get_api_key()
    if api_key:
        st.success("Google Gemini API Key Detected")
    else:
        st.warning("GEMINI_API_KEY not found in .env. Summarization & Gap Analysis will be disabled.")
        st.info("Get a free key at: https://aistudio.google.com/app/apikey")

    st.divider()
    st.markdown("### 🧠 System Architecture")
    st.markdown("""
    * **Module 1 (Search):** arXiv CSV Dataset (287,000+ papers) & arXiv API
    * **Module 2 (ML):** Sentence-BERT (`384D`) + Cosine Similarity
    * **Module 3 (AI):** Gemini LLM Structured Summarizer
    * **Module 4 (AI):** Multi-Paper Research Gap Synthesizer
    """)

# -------------------------------------------------------------
# SECTION 1: RESEARCH PAPER SEARCH (MODULE 1)
# -------------------------------------------------------------
st.header("1. 🔍 Search Research Papers")

search_source = st.radio(
    "Search Data Source:",
    options=["📁 arXiv CSV Dataset (287,000+ papers)", "🌐 arXiv Live API"],
    index=0,
    horizontal=True,
    help="Select whether to search the imported arXiv CSV dataset (ultra-fast) or live arXiv API."
)

col1, col2 = st.columns([3, 1])
with col1:
    topic_input = st.text_input("Enter Research Topic:", value="Generative AI in Education", placeholder="e.g. Generative AI in Education")
with col2:
    limit_input = st.number_input("Papers to retrieve:", min_value=2, max_value=20, value=5, step=1)

if st.button("Search Papers", type="primary"):
    if not topic_input.strip():
        st.error("Please enter a research topic to search.")
    else:
        src_key = "dataset" if "CSV" in search_source else "api"
        source_label = "arXiv CSV Dataset" if src_key == "dataset" else "arXiv API"
        with st.spinner(f"Searching {source_label} for '{topic_input}'..."):
            retrieved_papers = search_papers(topic_input.strip(), limit=int(limit_input), source=src_key)
            if retrieved_papers:
                st.session_state["papers"] = retrieved_papers
                st.session_state["last_topic"] = topic_input
                # Reset downstream state
                st.session_state["recommendations"] = []
                st.session_state["summaries"] = {}
                st.session_state["gap_report"] = ""
                st.success(f"Successfully retrieved {len(retrieved_papers)} research papers from {source_label}!")
            else:
                st.error("No papers found for this topic. Try a different research topic.")

# Display Retrieved Papers
if st.session_state["papers"]:
    papers = st.session_state["papers"]
    st.markdown(f"#### Retrieved Papers ({len(papers)})")

    for idx, paper in enumerate(papers, start=1):
        with st.expander(f"Paper #{idx}: {paper.get('title')}", expanded=(idx == 1)):
            st.markdown(f"**Authors:** {paper.get('authors')}")
            st.markdown(f"**Year:** {paper.get('year')}  |  **Paper ID:** `{paper.get('paperId')}`")
            st.markdown(f"**URL:** [{paper.get('url')}]({paper.get('url')})")
            abstract_text = paper.get("abstract", "Abstract not available.")
            st.markdown(f"**Abstract:** {abstract_text}")

    st.divider()

    # -------------------------------------------------------------
    # SECTION 2: PAPER SELECTION & RECOMMENDATION (MODULE 2 - ML)
    # -------------------------------------------------------------
    st.header("2. 🤖 ML-Based Paper Recommendation (Sentence-BERT)")

    paper_titles = [f"#{i+1}: {p.get('title')}" for i, p in enumerate(papers)]
    selected_paper_str = st.selectbox("Select a Primary Paper for Analysis:", options=paper_titles)
    selected_idx = paper_titles.index(selected_paper_str)
    selected_paper = papers[selected_idx]

    col_rec, col_sum = st.columns(2)

    with col_rec:
        if st.button("Find Similar Papers (Sentence-BERT)"):
            if len(papers) < 2:
                st.warning("Need at least 2 papers in search results to calculate similarity.")
            else:
                with st.spinner("Generating 384D Sentence-BERT embeddings & calculating cosine similarity..."):
                    top_n = min(3, len(papers) - 1)
                    recs = recommend_similar_papers(papers, selected_idx, top_n=top_n)
                    st.session_state["recommendations"] = recs

    # Display Recommendation Results
    if st.session_state["recommendations"]:
        st.subheader("Recommended Similar Papers")
        st.info("Similarity scores represent Cosine Similarity between 384-dimensional Sentence-BERT embeddings.")
        for r_idx, (rec_paper, score) in enumerate(st.session_state["recommendations"], start=1):
            pct = score * 100
            st.markdown(f"##### Recommendation #{r_idx}  |  Match: `{score:.4f}` ({pct:.1f}%)")
            st.markdown(f"**Title:** {rec_paper.get('title')}")
            st.markdown(f"**Year:** {rec_paper.get('year')}  |  **Authors:** {rec_paper.get('authors')}")
            st.markdown(f"**URL:** [{rec_paper.get('url')}]({rec_paper.get('url')})")
            st.caption(f"Abstract Snippet: {rec_paper.get('abstract')[:250]}...")
            st.markdown("---")

    # -------------------------------------------------------------
    # SECTION 3: AI PAPER SUMMARIZATION (MODULE 3 - GENAI)
    # -------------------------------------------------------------
    with col_sum:
        if st.button("Generate AI Structured Summary"):
            if not api_key:
                st.error("GEMINI_API_KEY environment variable is not set. Add your key to .env file.")
            else:
                with st.spinner("Generating 7-part AI structured summary using Gemini LLM..."):
                    summary_res = summarize_paper(
                        title=selected_paper.get("title", ""),
                        abstract=selected_paper.get("abstract", "")
                    )
                    st.session_state["summaries"][selected_paper.get("paperId")] = summary_res

    # Display Summary Results
    paper_id = selected_paper.get("paperId")
    if paper_id in st.session_state["summaries"]:
        st.subheader(f"AI Structured Summary: '{selected_paper.get('title')}'")
        st.markdown(st.session_state["summaries"][paper_id])

    st.divider()

    # -------------------------------------------------------------
    # SECTION 4: AI RESEARCH GAP IDENTIFICATION (MODULE 4 - GENAI)
    # -------------------------------------------------------------
    st.header("4. 🔬 AI-Based Potential Research Gap Identification")
    st.caption("Select 2 or more papers to analyze cross-paper themes, limitations, and potential research gaps.")

    selected_gap_paper_indices = st.multiselect(
        "Select papers for Research Gap Analysis:",
        options=list(range(len(papers))),
        format_func=lambda i: f"#{i+1}: {papers[i].get('title')}",
        default=list(range(min(5, len(papers))))
    )

    if st.button("Analyze Research Gaps", type="primary"):
        if len(selected_gap_paper_indices) < 2:
            st.warning("Please select at least 2 papers to perform multi-paper research gap analysis.")
        elif not api_key:
            st.error("GEMINI_API_KEY environment variable is not set. Add your key to .env file.")
        else:
            gap_papers = [papers[i] for i in selected_gap_paper_indices]
            with st.spinner(f"Analyzing potential research gaps across {len(gap_papers)} selected papers..."):
                gap_result = analyze_research_gaps(gap_papers)
                st.session_state["gap_report"] = gap_result

    # Display Research Gap Report
    if st.session_state["gap_report"]:
        st.subheader("Potential Research Gap & Future Direction Analysis")
        st.warning("⚠️ Disclaimer: Identifies potential research gaps based ONLY on the selected analyzed papers. Does not guarantee global research novelty.")
        st.markdown(st.session_state["gap_report"])
