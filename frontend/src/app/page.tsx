"use client";

import { useEffect, useState } from "react";
import { Separator } from "@/components/ui/separator";
import { StatusBar } from "@/components/status-bar";
import { SearchSection } from "@/components/sections/search-section";
import { RecommendSection } from "@/components/sections/recommend-section";
import { SummarySection } from "@/components/sections/summary-section";
import { GapSection } from "@/components/sections/gap-section";
import { getStatus, type Paper, type Recommendation, type Status } from "@/lib/api";

export default function Home() {
  const [status, setStatus] = useState<Status | null>(null);
  const [statusError, setStatusError] = useState("");

  const [papers, setPapers] = useState<Paper[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [summaries, setSummaries] = useState<Record<string, string>>({});
  const [gapReport, setGapReport] = useState("");
  const [searchKey, setSearchKey] = useState(0);

  useEffect(() => {
    let active = true;

    getStatus()
      .then((result) => {
        if (active) setStatus(result);
      })
      .catch((err: Error) => {
        if (active) setStatusError(err.message);
      });

    return () => {
      active = false;
    };
  }, []);

  function handleResults(next: Paper[]) {
    setPapers(next);
    setRecommendations([]);
    setSummaries({});
    setGapReport("");
    setSearchKey((current) => current + 1);
  }

  const apiKeyReady = status?.apiKeyConfigured ?? false;

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="border-b">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-6 py-8 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex flex-col gap-1.5">
            <span className="text-[0.7rem] font-medium tracking-[0.18em] text-muted-foreground uppercase">
              ResearchMind AI
            </span>
            <h1 className="text-2xl font-medium tracking-tight">Research workspace</h1>
            <p className="max-w-xl text-sm text-muted-foreground">
              Search papers, rank semantic recommendations, generate structured summaries and surface potential
              research gaps.
            </p>
          </div>
          <StatusBar status={status} error={statusError} />
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-12 px-6 py-10">
        <SearchSection papers={papers} onResults={handleResults} />

        {papers.length > 0 ? (
          <>
            <Separator />
            <RecommendSection
              key={`recommend-${searchKey}`}
              papers={papers}
              recommendations={recommendations}
              onResult={setRecommendations}
            />
            <Separator />
            <SummarySection
              key={`summary-${searchKey}`}
              papers={papers}
              summaries={summaries}
              apiKeyReady={apiKeyReady}
              onResult={(paperId, summary) =>
                setSummaries((current) => ({ ...current, [paperId]: summary }))
              }
            />
            <Separator />
            <GapSection
              key={`gap-${searchKey}`}
              papers={papers}
              report={gapReport}
              apiKeyReady={apiKeyReady}
              onResult={setGapReport}
            />
          </>
        ) : (
          <div className="rounded-xl border border-dashed px-6 py-12 text-center text-sm text-muted-foreground">
            Run a search to load papers. Recommendation, summarization and research gap tools appear here.
          </div>
        )}
      </main>

      <footer className="border-t">
        <div className="mx-auto flex w-full max-w-5xl flex-wrap items-center justify-between gap-2 px-6 py-5 text-xs text-muted-foreground">
          <span>Modules: search, recommendation, summarization, research gap.</span>
          <span>FastAPI + Next.js + shadcn/ui</span>
        </div>
      </footer>
    </div>
  );
}
