"use client";

import { useState } from "react";
import { SparklesIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Busy, ErrorNote, Section } from "@/components/section";
import { recommendPapers, type Paper, type Recommendation } from "@/lib/api";

function truncate(text: string, max = 96) {
  return text.length > max ? `${text.slice(0, max).trimEnd()}...` : text;
}

export function RecommendSection({
  papers,
  recommendations,
  onResult,
}: {
  papers: Paper[];
  recommendations: Recommendation[];
  onResult: (recommendations: Recommendation[]) => void;
}) {
  const [targetIndex, setTargetIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const insufficient = papers.length < 2;

  async function handleRecommend() {
    setLoading(true);
    setError("");

    try {
      const result = await recommendPapers(papers, targetIndex, 3);
      onResult(result.recommendations);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Recommendation failed.");
      onResult([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Section
      step="02 / Recommendation"
      title="Semantic paper recommendations"
      description="Sentence-BERT embeddings (384 dimensions) ranked by cosine similarity against the selected paper."
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex flex-1 flex-col gap-1.5">
          <span className="text-sm font-medium">Primary paper</span>
          <Select value={String(targetIndex)} onValueChange={(value) => setTargetIndex(Number(value))}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select a paper" />
            </SelectTrigger>
            <SelectContent>
              {papers.map((paper, index) => (
                <SelectItem key={`${paper.paperId}-${index}`} value={String(index)}>
                  {truncate(`#${index + 1}: ${paper.title}`)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button size="lg" onClick={handleRecommend} disabled={loading || insufficient}>
          <SparklesIcon />
          {loading ? "Ranking" : "Find similar papers"}
        </Button>
      </div>

      {insufficient ? (
        <p className="text-sm text-muted-foreground">
          At least 2 papers are required to calculate similarity.
        </p>
      ) : null}

      {loading ? (
        <Busy label="Generating 384D Sentence-BERT embeddings and computing cosine similarity" />
      ) : null}

      {error ? <ErrorNote message={error} /> : null}

      {!loading && recommendations.length > 0 ? (
        <div className="flex flex-col gap-3">
          <p className="text-xs font-medium tracking-[0.14em] text-muted-foreground uppercase">
            Ranked matches ({recommendations.length})
          </p>

          {recommendations.map((item, index) => {
            const percent = Math.max(0, Math.min(100, item.score * 100));

            return (
              <Card key={`${item.paper.paperId}-${index}`} size="sm">
                <CardHeader>
                  <CardTitle>{item.paper.title}</CardTitle>
                  <CardDescription>{item.paper.authors}</CardDescription>
                  <CardAction>
                    <Badge variant="secondary" className="font-mono">
                      {percent.toFixed(1)}% match
                    </Badge>
                  </CardAction>
                </CardHeader>

                <CardContent className="flex flex-col gap-3">
                  <Progress value={percent} aria-label={`Similarity ${percent.toFixed(1)} percent`} />
                  <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground">
                    <span>
                      {item.paper.year} / cosine similarity {item.score.toFixed(4)}
                    </span>
                    <a
                      href={item.paper.url}
                      target="_blank"
                      rel="noreferrer"
                      className="underline underline-offset-4 hover:text-foreground"
                    >
                      Open paper
                    </a>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : null}
    </Section>
  );
}
