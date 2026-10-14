"use client";

import { useState } from "react";
import { ArrowUpRightIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { Paper } from "@/lib/api";

export function PaperList({ papers }: { papers: Paper[] }) {
  const [expandedId, setExpandedId] = useState<string | null>(papers[0]?.paperId ?? null);

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-medium tracking-[0.14em] text-muted-foreground uppercase">
        Retrieved papers ({papers.length})
      </p>

      {papers.map((paper, index) => {
        const expanded = paper.paperId === expandedId;

        return (
          <Card key={`${paper.paperId}-${index}`} size="sm">
            <CardHeader>
              <CardTitle>{paper.title}</CardTitle>
              <CardDescription>{paper.authors}</CardDescription>
              <CardAction className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setExpandedId(expanded ? null : paper.paperId)}
                >
                  {expanded ? "Hide abstract" : "Abstract"}
                </Button>
                <Button variant="ghost" size="icon-sm" asChild>
                  <a href={paper.url} target="_blank" rel="noreferrer" aria-label="Open paper on arXiv">
                    <ArrowUpRightIcon />
                  </a>
                </Button>
              </CardAction>
            </CardHeader>

            <CardContent className="flex flex-col gap-3">
              <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                <Badge variant="outline" className="font-mono">
                  #{index + 1}
                </Badge>
                <span>{paper.year}</span>
                <span aria-hidden="true">/</span>
                <span>{paper.category}</span>
              </div>

              {expanded ? (
                <p className="text-sm leading-relaxed text-muted-foreground">{paper.abstract}</p>
              ) : null}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
