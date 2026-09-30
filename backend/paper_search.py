import os
import re
import requests
import xml.etree.ElementTree as ET
import pandas as pd

# Base URL for arXiv API endpoint (Open Academic Research Repository)
BASE_URL = "http://export.arxiv.org/api/query"
DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "arXiv_scientific_dataset.csv")

# Global cache for the DataFrame to avoid reading 400MB CSV on every search
_cached_dataset_df = None


def extract_year(date_val):
    """
    Extract a 4-digit year string from various date formats in CSV.
    """
    if pd.isna(date_val) or not date_val:
        return "N/A"
    s = str(date_val).strip()
    parts = s.replace('-', '/').split('/')
    if len(parts) >= 3:
        last = parts[-1].strip()
        if len(last) == 4 and last.isdigit():
            return last
        if len(last) == 2 and last.isdigit():
            yy = int(last)
            return f"19{yy}" if yy > 50 else f"20{yy:02d}"
    if len(parts[0]) == 4 and parts[0].isdigit():
        return parts[0]
    return s[:4] if len(s) >= 4 else s


def load_dataset(csv_path=DATASET_PATH):
    """
    Loads and caches the arXiv CSV dataset from dataset folder.

    Returns:
        pd.DataFrame or None if file not found.
    """
    global _cached_dataset_df
    if _cached_dataset_df is not None:
        return _cached_dataset_df

    if not os.path.exists(csv_path):
        print(f"\n[!] Dataset CSV file not found at: '{csv_path}'")
        return None

    print(f"\n[+] Loading arXiv dataset from '{csv_path}'...")
    try:
        df = pd.read_csv(csv_path)

        # Pre-build search_text column for fast text matching
        df['search_text'] = (
            df['title'].fillna('') + ' ' +
            df['summary'].fillna('') + ' ' +
            df['category'].fillna('') + ' ' +
            df['authors'].fillna('') + ' ' +
            df['id'].fillna('')
        ).str.lower()

        _cached_dataset_df = df
        print(f"[+] Loaded {len(df):,} papers from arXiv dataset.")
        return _cached_dataset_df
    except Exception as e:
        print(f"\n[!] Error loading CSV dataset: {e}")
        return None


def search_papers_csv(query, limit=5, dataset_path=DATASET_PATH):
    """
    Search research papers in local arXiv CSV dataset by topic query.

    Parameters:
        query (str): Research topic query.
        limit (int): Max papers to return.
        dataset_path (str): Path to CSV dataset.

    Returns:
        list: List of paper dicts.
    """
    df = load_dataset(dataset_path)
    if df is None or df.empty:
        return []

    query_clean = query.strip().lower()
    if not query_clean:
        return []

    stop_words = {'in', 'on', 'at', 'of', 'for', 'with', 'a', 'an', 'the', 'and', 'or', 'to', 'is', 'are', 'by', 'from'}
    terms = [w for w in re.findall(r'\w+', query_clean) if len(w) > 1 and w not in stop_words]
    if not terms:
        terms = re.findall(r'\w+', query_clean)

    # 1. Check exact match in title or ID
    mask_exact = df['title'].fillna('').str.lower().str.contains(re.escape(query_clean)) | (df['id'].fillna('').str.lower() == query_clean)

    # 2. Check all terms matching in search_text
    mask_all_terms = df['search_text'].apply(lambda text: all(term in text for term in terms))

    matching_df = df[mask_exact | mask_all_terms].copy()

    # Fallback to ANY term matching if matches are fewer than limit
    if len(matching_df) < limit and terms:
        mask_any_terms = df['search_text'].apply(lambda text: any(term in text for term in terms))
        matching_df = df[mask_any_terms].copy()

    if matching_df.empty:
        return []

    # Score candidates for relevance ranking
    def score_row(row):
        score = 0
        t = str(row.get('title', '')).lower()
        s = str(row.get('summary', '')).lower()
        cat = str(row.get('category', '')).lower()

        if query_clean in t:
            score += 100
        if query_clean in s:
            score += 40
        if query_clean in cat:
            score += 30

        for term in terms:
            if term in t:
                score += 10
            if term in s:
                score += 4
            if term in cat:
                score += 5
        return score

    matching_df['relevance'] = matching_df.apply(score_row, axis=1)
    sorted_df = matching_df.sort_values(by='relevance', ascending=False).head(limit)

    papers = []
    for _, row in sorted_df.iterrows():
        raw_id = str(row.get('id', 'N/A')).strip()
        clean_id = raw_id.split('/abs/')[-1] if '/abs/' in raw_id else raw_id
        url = f"https://arxiv.org/abs/{clean_id}"
        year = extract_year(row.get('published_date'))

        title = str(row.get('title', 'No Title Available')).strip().replace('\n', ' ')
        abstract = str(row.get('summary', 'No abstract available for this paper.')).strip().replace('\n', ' ')
        authors = str(row.get('authors', 'Unknown Author(s)')).strip()

        papers.append({
            "paperId": raw_id,
            "title": title,
            "authors": authors,
            "year": year,
            "url": url,
            "abstract": abstract,
            "category": str(row.get('category', 'N/A'))
        })

    return papers


def search_papers_api(query, limit=5):
    """
    Search research papers on arXiv API by research topic query.
    """
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit
    }

    headers = {
        "User-Agent": "ResearchMindAI/1.0"
    }

    print(f"\n[+] Searching arXiv Academic Repository API for: '{query}'...")

    try:
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        papers = []
        for entry in root.findall("atom:entry", ns):
            raw_id = entry.find("atom:id", ns).text.strip() if entry.find("atom:id", ns) is not None else "N/A"
            paper_id = raw_id.split("/abs/")[-1] if "/abs/" in raw_id else raw_id

            title_elem = entry.find("atom:title", ns)
            title = title_elem.text.strip().replace("\n", " ") if title_elem is not None and title_elem.text else "No Title Available"

            published_elem = entry.find("atom:published", ns)
            year = published_elem.text[:4] if published_elem is not None and published_elem.text else "N/A"

            url = raw_id

            summary_elem = entry.find("atom:summary", ns)
            abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None and summary_elem.text else "No abstract available for this paper."

            authors = []
            for author_elem in entry.findall("atom:author", ns):
                name_elem = author_elem.find("atom:name", ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())

            author_names = ", ".join(authors) if authors else "Unknown Author(s)"

            papers.append({
                "paperId": paper_id,
                "title": title,
                "authors": author_names,
                "year": year,
                "url": url,
                "abstract": abstract,
                "category": "arXiv API"
            })

        return papers

    except Exception as e:
        print(f"\n[!] API Request Error: {e}")
        return []


def search_papers(query, limit=5, source="dataset"):
    """
    Unified search entrypoint supporting both local CSV dataset and arXiv API.

    Parameters:
        query (str): Search term/topic.
        limit (int): Number of papers to retrieve.
        source (str): 'dataset' for local CSV, 'api' for live arXiv API.
    """
    if source == "dataset":
        print(f"\n[+] Searching local CSV dataset for: '{query}'...")
        results = search_papers_csv(query, limit=limit)
        if results:
            return results
        print("\n[!] No results from dataset or dataset file missing. Falling back to arXiv API...")
        return search_papers_api(query, limit=limit)
    else:
        return search_papers_api(query, limit=limit)


def display_papers(papers):
    """
    Format and display research paper details clearly in console.
    """
    if not papers:
        print("\n[!] No research papers found for this topic.")
        return

    print(f"\n{'=' * 75}")
    print(f" FOUND {len(papers)} RESEARCH PAPERS ")
    print(f"{'=' * 75}\n")

    for idx, paper in enumerate(papers, start=1):
        title = paper.get("title", "No Title Available")
        paper_id = paper.get("paperId", "N/A")
        year = paper.get("year", "N/A")
        url = paper.get("url", "N/A")
        abstract = paper.get("abstract")

        if not abstract:
            abstract = "No abstract available for this paper."

        print(f"Paper #{idx}: {title}")
        print(f"  • Paper ID    : {paper_id}")
        print(f"  • Category    : {paper.get('category', 'N/A')}")
        print(f"  • Authors     : {paper.get('authors', 'Unknown')}")
        print(f"  • Year        : {year}")
        print(f"  • URL         : {url}")
        print(f"  • Abstract    : {abstract[:300]}..." if len(abstract) > 300 else f"  • Abstract    : {abstract}")
        print("-" * 75)


def main():
    """
    Main interactive function to run Module 1.
    """
    print("=" * 60)
    print(" ResearchMind AI — Module 1: Research Paper Search")
    print("=" * 60)

    src_choice = input("\nSelect Search Source [1: CSV Dataset (Default), 2: arXiv API]: ").strip()
    source = "api" if src_choice == "2" else "dataset"

    topic = input("\nEnter research topic (e.g., Generative AI in Education): ").strip()
    if not topic:
        print("[!] Topic cannot be empty. Exiting...")
        return

    limit_input = input("Enter number of papers to retrieve (default is 5): ").strip()
    if not limit_input:
        limit = 5
    else:
        try:
            limit = int(limit_input)
            if limit <= 0:
                print("[!] Number must be positive. Defaulting to 5.")
                limit = 5
        except ValueError:
            print("[!] Invalid input. Defaulting to 5.")
            limit = 5

    papers = search_papers(topic, limit=limit, source=source)
    display_papers(papers)


if __name__ == "__main__":
    main()
