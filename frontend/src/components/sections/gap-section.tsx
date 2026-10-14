"use client";

import { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Busy, ErrorNote, Section } from "@/components/section";
import { Report } from "@/components/report";
import { analyzeGaps, type Paper } from "@/lib/api";

const DEFAULT_SELECTION = 5;

export function GapSection({
  papers,
  report,
  apiKeyReady,
  onResult,
}: {
  papers: Paper[];
  report: string;
  apiKeyReady: boolean;
  onResult: (report: string) => void;
}) {
  const [selected, setSelected] = useState<number[]>(() =>
    Array.from({ length: Math.min(DEFAULT_SELECTION, papers.length) }, (_, index) => index),
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const insufficient = selected.length < 2;

  function toggle(index: number) {
    setSelected((current) =>
      current.includes(index) ? current.filter((item) => item !== index) : [...current, index].sort((a, b) => a - b),
    );
  }

  async function handleAnalyze() {
    const chosen = selected.map((index) => papers[index]).filter(Boolean);
    if (chosen.length < 2) return;

    setLoading(true);
    setError("");

    try {
      const result = await analyzeGaps(chosen);
      onResult(result.text);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Research gap analysis failed.");
      onResult("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Section
      step="04 / Research gaps"
      title="Potential research gap analysis"
      description="Cross-paper synthesis of themes, limitations, gaps and future directions across two or more selected papers."
    >
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-3">
          <span className="text-sm font-medium">Papers selected ({selected.length})</span>
          <div className="flex items-center gap-3 text-xs">
            <button
              type="button"
              className="text-muted-foreground underline underline-offset-4 hover:text-foreground"
              onClick={() => setSelected(papers.map((_, index) => index))}
            >
              Select all
            </button>
            <button
              type="button"
              className="text-muted-foreground underline underline-offset-4 hover:text-foreground"
              onClick={() => setSelected([])}
            >
              Clear
            </button>
          </div>
        </div>

        <div className="grid gap-2">
          {papers.map((paper, index) => {
            const checked = selected.includes(index);

            return (
              <div
                key={`${paper.paperId}-${index}`}
                onClick={() => toggle(index)}
                className={`flex cursor-pointer items-start gap-3 rounded-lg border px-3 py-2.5 transition-colors ${
                  checked ? "border-foreground/25 bg-muted/60" : "hover:bg-muted/50"
                }`}
              >
                <Checkbox
                  checked={checked}
                  onCheckedChange={() => toggle(index)}
                  onClick={(event) => event.stopPropagation()}
                  aria-label={`Select ${paper.title}`}
                />
                <span className="flex min-w-0 flex-col gap-0.5">
                  <span className="text-sm leading-snug font-medium">
                    #{index + 1} {paper.title}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {paper.year} / {paper.authors}
                  </span>
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <Button size="lg" onClick={handleAnalyze} disabled={loading || insufficient || !apiKeyReady}>
          Analyze research gaps
        </Button>
        {insufficient ? (
          <p className="text-sm text-muted-foreground">Select at least 2 papers to run the analysis.</p>
        ) : null}
        {!apiKeyReady ? (
          <p className="text-sm text-muted-foreground">GEMINI_API_KEY is required for gap analysis.</p>
        ) : null}
      </div>

      {loading ? <Busy label="Synthesizing themes, limitations and gaps across the selected papers" /> : null}
      {error ? <ErrorNote message={error} /> : null}

      {!loading && report ? (
        <div className="flex flex-col gap-3">
          <Card size="sm">
            <CardHeader>
              <CardTitle>Research gap report</CardTitle>
            </CardHeader>
            <CardContent>
              <Report text={report} />
            </CardContent>
          </Card>
          <p className="text-xs text-muted-foreground">
            Disclaimer: identifies potential research gaps based only on the selected papers. It does not guarantee
            global research novelty.
          </p>
        </div>
      ) : null}
    </Section>
  );
}
