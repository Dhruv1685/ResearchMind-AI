export type Paper = {
  paperId: string;
  title: string;
  authors: string;
  year: string;
  url: string;
  abstract: string;
  category: string;
};

export type Recommendation = {
  paper: Paper;
  score: number;
};

export type SearchSource = "dataset" | "api";

export type Status = {
  apiKeyConfigured: boolean;
  datasetAvailable: boolean;
  modules: string[];
};

export type SearchResponse = {
  papers: Paper[];
  count: number;
  source: string;
  query: string;
};

export type RecommendResponse = {
  recommendations: Recommendation[];
  count: number;
};

export type TextResponse = {
  text: string;
  ok: boolean;
};

const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");

async function request<T>(path: string, body?: unknown): Promise<T> {
  let response: Response;

  try {
    response =
      body === undefined
        ? await fetch(`${API_BASE}${path}`, { cache: "no-store" })
        : await fetch(`${API_BASE}${path}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          });
  } catch {
    throw new Error("API server is not reachable. Start it with: python server.py");
  }

  const payload = (await response.json().catch(() => null)) as Record<string, unknown> | null;

  if (!response.ok) {
    const detail = payload?.detail;
    throw new Error(typeof detail === "string" ? detail : `Request failed with status ${response.status}`);
  }

  return payload as T;
}

export function getStatus(): Promise<Status> {
  return request<Status>("/api/status");
}

export function searchPapers(query: string, limit: number, source: SearchSource): Promise<SearchResponse> {
  return request<SearchResponse>("/api/search", { query, limit, source });
}

export function recommendPapers(papers: Paper[], targetIndex: number, topN = 3): Promise<RecommendResponse> {
  return request<RecommendResponse>("/api/recommend", {
    papers,
    target_index: targetIndex,
    top_n: topN,
  });
}

export function summarizePaper(title: string, abstract: string): Promise<TextResponse> {
  return request<{ summary: string; ok: boolean }>("/api/summarize", { title, abstract }).then((res) => ({
    text: res.summary ?? "",
    ok: res.ok,
  }));
}

export function analyzeGaps(papers: Paper[]): Promise<TextResponse> {
  return request<{ report: string; ok: boolean }>("/api/gap", { papers }).then((res) => ({
    text: res.report ?? "",
    ok: res.ok,
  }));
}
