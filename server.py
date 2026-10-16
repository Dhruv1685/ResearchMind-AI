"""
ResearchMind AI - FastAPI backend server.

Exposes Module 1 (Search), Module 2 (ML Recommendation),
Module 3 (AI Summarization) and Module 4 (Research Gap Discovery)
as REST endpoints consumed by the shadcn/ui dashboard.
"""

import os
import threading
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.paper_recommender import recommend_similar_papers
from backend.paper_search import DATASET_PATH, search_papers
from backend.paper_summarizer import get_api_key, summarize_paper
from backend.research_gap import analyze_research_gaps

load_dotenv()

LOCAL_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


def build_allowed_origins() -> list[str]:
    """Comma-separated ALLOWED_ORIGINS env var, otherwise allow any origin."""
    raw = os.environ.get("ALLOWED_ORIGINS", "").strip()
    if not raw:
        return ["*"]
    return LOCAL_ORIGINS + [origin.strip() for origin in raw.split(",") if origin.strip()]


def warm_models() -> None:
    """Pre-load the Sentence-BERT model so the first recommendation is fast."""
    if os.environ.get("WARM_MODELS", "1").strip().lower() in ("0", "false", "no"):
        return
    try:
        from backend.paper_recommender import get_model

        get_model()
        print("[+] Sentence-BERT model warmed up.")
    except Exception as exc:
        print(f"[!] Model warm-up skipped: {exc}")


@asynccontextmanager
async def lifespan(_: FastAPI):
    threading.Thread(target=warm_models, daemon=True).start()
    yield


app = FastAPI(title="ResearchMind AI API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=build_allowed_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Paper(BaseModel):
    paperId: str = ""
    title: str = ""
    authors: str = ""
    year: str = ""
    url: str = ""
    abstract: str = ""
    category: str = ""


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=300)
    limit: int = Field(default=5, ge=2, le=20)
    source: str = Field(default="dataset")


class RecommendRequest(BaseModel):
    papers: list[Paper]
    target_index: int = Field(ge=0)
    top_n: int = Field(default=3, ge=1, le=10)


class SummarizeRequest(BaseModel):
    title: str = ""
    abstract: str = ""


class GapRequest(BaseModel):
    papers: list[Paper] = Field(min_length=2)


def _is_error_message(text: str) -> bool:
    return text.strip().startswith("[!]")


@app.get("/api/status")
def status():
    return {
        "apiKeyConfigured": bool(get_api_key()),
        "datasetAvailable": os.path.exists(DATASET_PATH),
        "modules": [
            "Search",
            "Recommendation",
            "Summarization",
            "Research Gap",
        ],
    }


@app.post("/api/search")
def search(req: SearchRequest):
    source = req.source if req.source in ("dataset", "api") else "dataset"
    dataset_present = os.path.exists(DATASET_PATH)
    try:
        papers = search_papers(req.query.strip(), limit=req.limit, source=source)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}") from exc

    effective_source = "dataset" if source == "dataset" and dataset_present else "api"

    return {
        "papers": [p.model_dump() if isinstance(p, Paper) else p for p in papers],
        "count": len(papers),
        "source": effective_source,
        "query": req.query.strip(),
    }


@app.post("/api/recommend")
def recommend(req: RecommendRequest):
    if len(req.papers) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 papers are required to calculate similarity.",
        )
    if req.target_index >= len(req.papers):
        raise HTTPException(status_code=400, detail="Selected paper index is out of range.")

    papers = [p.model_dump() for p in req.papers]
    top_n = min(req.top_n, len(papers) - 1)

    try:
        results = recommend_similar_papers(papers, req.target_index, top_n=top_n)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {exc}") from exc

    return {
        "recommendations": [
            {"paper": paper, "score": round(float(score), 6)}
            for paper, score in results
        ],
        "count": len(results),
    }


@app.post("/api/summarize")
def summarize(req: SummarizeRequest):
    if not get_api_key():
        raise HTTPException(
            status_code=400,
            detail="GEMINI_API_KEY is not configured. Add it to your .env file.",
        )

    try:
        summary = summarize_paper(title=req.title, abstract=req.abstract)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {exc}") from exc

    return {"summary": summary, "ok": not _is_error_message(summary)}


@app.post("/api/gap")
def gap(req: GapRequest):
    if len(req.papers) < 2:
        raise HTTPException(
            status_code=400,
            detail="Research gap analysis requires at least 2 papers.",
        )
    if not get_api_key():
        raise HTTPException(
            status_code=400,
            detail="GEMINI_API_KEY is not configured. Add it to your .env file.",
        )

    papers = [p.model_dump() for p in req.papers]

    try:
        report = analyze_research_gaps(papers)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gap analysis failed: {exc}") from exc

    return {"report": report, "ok": not _is_error_message(report)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), reload=False)
