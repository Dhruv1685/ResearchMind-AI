"use client";

import { useState } from "react";
import { SearchIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Busy, ErrorNote, Section, SuccessNote } from "@/components/section";
import { PaperList } from "@/components/paper-list";
import { searchPapers, type Paper, type SearchSource } from "@/lib/api";

const SOURCE_LABEL: Record<SearchSource, string> = {
  dataset: "arXiv CSV dataset",
  api: "arXiv API",
};

export function SearchSection({
  papers,
  datasetAvailable,
  onResults,
}: {
  papers: Paper[];
  datasetAvailable: boolean | null;
  onResults: (papers: Paper[]) => void;
}) {
  const [source, setSource] = useState<SearchSource>("dataset");
  const [query, setQuery] = useState("Generative AI in Education");
  const [limit, setLimit] = useState("5");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [searchKey, setSearchKey] = useState(0);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmed = query.trim();
    if (!trimmed) {
      setError("Enter a research topic to search.");
      setNotice("");
      return;
    }

    const parsedLimit = Number.parseInt(limit, 10);
    const safeLimit = Number.isFinite(parsedLimit) ? Math.min(20, Math.max(2, parsedLimit)) : 5;

    setLoading(true);
    setError("");
    setNotice("");

    try {
      const result = await searchPapers(trimmed, safeLimit, source);

      if (result.papers.length === 0) {
        setError("No papers found for this topic. Try a different research topic.");
        setNotice("");
        return;
      }

      onResults(result.papers);
      setSearchKey((current) => current + 1);
      const used = SOURCE_LABEL[result.source as SearchSource] ?? "arXiv API";
      setNotice(`Retrieved ${result.papers.length} papers from ${used}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Section
      step="01 / Search"
      title="Find research papers"
      description="Search the local arXiv CSV dataset with 287,000+ papers, or query the live arXiv API."
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Tabs value={source} onValueChange={(value) => setSource(value as SearchSource)}>
          <TabsList>
            <TabsTrigger value="dataset">CSV dataset</TabsTrigger>
            <TabsTrigger value="api">arXiv API</TabsTrigger>
          </TabsList>
        </Tabs>

        {datasetAvailable === false ? (
          <p className="text-sm text-muted-foreground">
            CSV dataset not found in this environment. Searches run against the live arXiv API.
          </p>
        ) : null}

        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex flex-1 flex-col gap-1.5">
            <Label htmlFor="topic">Research topic</Label>
            <Input
              id="topic"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="e.g. Generative AI in Education"
              autoComplete="off"
            />
          </div>

          <div className="flex w-full flex-col gap-1.5 sm:w-28">
            <Label htmlFor="limit">Papers</Label>
            <Input
              id="limit"
              type="number"
              min={2}
              max={20}
              value={limit}
              onChange={(event) => setLimit(event.target.value)}
            />
          </div>

          <Button type="submit" size="lg" disabled={loading}>
            <SearchIcon />
            {loading ? "Searching" : "Search papers"}
          </Button>
        </div>
      </form>

      {loading ? <Busy label={`Searching ${SOURCE_LABEL[source]} for "${query.trim()}"`} /> : null}
      {error ? <ErrorNote message={error} /> : null}
      {!loading && !error && notice ? <SuccessNote message={notice} /> : null}

      {papers.length > 0 ? <PaperList key={searchKey} papers={papers} /> : null}
    </Section>
  );
}
