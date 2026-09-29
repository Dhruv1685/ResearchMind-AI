import requests
import xml.etree.ElementTree as ET
import json

# Base URL for arXiv API endpoint (Open Academic Research Repository)
BASE_URL = "http://export.arxiv.org/api/query"


def search_papers(query, limit=5):
    """
    Search research papers on arXiv API by research topic query.

    Parameters:
        query (str): Research topic entered by user.
        limit (int): Number of papers to retrieve (default 5).

    Returns:
        list: List of dictionaries containing paper details, or empty list on failure.
    """
    # Parameters for arXiv API
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit
    }

    headers = {
        "User-Agent": "ResearchMindAI/1.0"
    }

    print(f"\n[+] Searching arXiv Academic Repository for: '{query}'...")

    try:
        # Send HTTP GET request to arXiv API
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=10)

        # Raise exception for HTTP status errors (4xx, 5xx)
        response.raise_for_status()

        # Parse XML response using Python's built-in ElementTree
        root = ET.fromstring(response.text)

        # XML namespace used by arXiv Atom feed
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        papers = []

        # Find all paper entries in the XML feed
        for entry in root.findall("atom:entry", ns):
            # Extract Paper ID (clean ID from full URL)
            raw_id = entry.find("atom:id", ns).text.strip() if entry.find("atom:id", ns) is not None else "N/A"
            paper_id = raw_id.split("/abs/")[-1] if "/abs/" in raw_id else raw_id

            # Extract Title
            title_elem = entry.find("atom:title", ns)
            title = title_elem.text.strip().replace("\n", " ") if title_elem is not None and title_elem.text else "No Title Available"

            # Extract Publication Year (4-digit year)
            published_elem = entry.find("atom:published", ns)
            year = published_elem.text[:4] if published_elem is not None and published_elem.text else "N/A"

            # Paper URL
            url = raw_id

            # Extract Abstract (Summary)
            summary_elem = entry.find("atom:summary", ns)
            abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None and summary_elem.text else "No abstract available for this paper."

            # Extract Author Names
            authors = []
            for author_elem in entry.findall("atom:author", ns):
                name_elem = author_elem.find("atom:name", ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())

            author_names = ", ".join(authors) if authors else "Unknown Author(s)"

            # Build paper dictionary
            papers.append({
                "paperId": paper_id,
                "title": title,
                "authors": author_names,
                "year": year,
                "url": url,
                "abstract": abstract
            })

        return papers

    except requests.exceptions.ConnectionError:
        print("\n[!] Network Error: Unable to connect to the internet. Please check your connection.")
        return []
    except requests.exceptions.Timeout:
        print("\n[!] Timeout Error: The arXiv API server took too long to respond.")
        return []
    except requests.exceptions.HTTPError as http_err:
        print(f"\n[!] HTTP Error occurred: {http_err}")
        return []
    except ET.ParseError:
        print("\n[!] Parsing Error: Failed to parse XML response from arXiv.")
        return []
    except requests.exceptions.RequestException as req_err:
        print(f"\n[!] API Request Error: {req_err}")
        return []


def display_papers(papers):
    """
    Format and display research paper details clearly in console.

    Parameters:
        papers (list): List of paper dictionaries returned by search_papers().
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

        # Handle missing or empty abstract gracefully
        if not abstract:
            abstract = "No abstract available for this paper."

        # Display formatted paper information
        print(f"Paper #{idx}: {title}")
        print(f"  • Paper ID    : {paper_id}")
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

    # Ask user for research topic
    topic = input("\nEnter research topic (e.g., Generative AI in Education): ").strip()

    if not topic:
        print("[!] Topic cannot be empty. Exiting...")
        return

    # Ask user for paper limit with 5 as default
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

    # Fetch papers from API
    papers = search_papers(topic, limit)

    # Display papers
    display_papers(papers)


if __name__ == "__main__":
    main()
