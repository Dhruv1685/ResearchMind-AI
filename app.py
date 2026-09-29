"""
ResearchMind AI — Main Application Entry Point
Integrates Module 1 (Paper Search), Module 2 (ML Recommendation), & Module 3 (AI Summarization)
"""

from backend.paper_search import search_papers, display_papers
from backend.paper_recommender import recommend_similar_papers
from backend.paper_summarizer import summarize_paper


def main():
    print("=" * 75)
    print(" ResearchMind AI — Intelligent Research Paper Search, Recommender & Summarizer")
    print("=" * 75)

    # -------------------------------------------------------------
    # MODULE 1: PAPER SEARCH
    # -------------------------------------------------------------
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
                limit = 5
        except ValueError:
            limit = 5

    # Fetch papers using arXiv API
    papers = search_papers(topic, limit)

    if not papers:
        print("[!] No papers retrieved. Exiting...")
        return

    # Display retrieved papers
    display_papers(papers)

    # -------------------------------------------------------------
    # PAPER SELECTION & ACTION MENU
    # -------------------------------------------------------------
    while True:
        try:
            choice = input(f"\nSelect a paper number (1 to {len(papers)}) to analyze: ").strip()
            paper_num = int(choice)
            if 1 <= paper_num <= len(papers):
                target_index = paper_num - 1
                break
            else:
                print(f"[!] Please enter a number between 1 and {len(papers)}.")
        except ValueError:
            print("[!] Invalid input. Please enter a valid integer.")

    selected_paper = papers[target_index]
    print(f"\n[+] Selected Paper #{paper_num}: '{selected_paper.get('title')}'")

    print("\nSelect an action:")
    print("  [1] Generate AI Structured Summary (Module 3)")
    print("  [2] Find Similar Recommended Papers (Module 2)")
    print("  [3] Both (Summarize + Recommend)")

    action = input("\nEnter choice (1, 2, or 3): ").strip()

    # -------------------------------------------------------------
    # MODULE 3: AI SUMMARIZATION
    # -------------------------------------------------------------
    if action in ["1", "3"]:
        print("\n" + "=" * 75)
        print(" MODULE 3: AI-POWERED PAPER SUMMARIZATION")
        print("=" * 75)

        summary = summarize_paper(
            title=selected_paper.get("title", ""),
            abstract=selected_paper.get("abstract", "")
        )

        print("\n" + summary)

    # -------------------------------------------------------------
    # MODULE 2: ML RECOMMENDATION
    # -------------------------------------------------------------
    if action in ["2", "3"]:
        if len(papers) < 2:
            print("\n[!] Need at least 2 papers in search results to perform recommendation.")
            return

        print("\n" + "=" * 75)
        print(" MODULE 2: ML-BASED PAPER RECOMMENDATION")
        print("=" * 75)

        top_n = min(3, len(papers) - 1)
        recommendations = recommend_similar_papers(papers, target_index, top_n=top_n)

        print(f"\n{'=' * 75}")
        print(f" TOP {len(recommendations)} RECOMMENDED SIMILAR PAPERS ")
        print(f"{'=' * 75}\n")

        for idx, (paper, score) in enumerate(recommendations, start=1):
            percentage = score * 100
            print(f"Recommendation #{idx}  |  Similarity Score: {score:.4f} ({percentage:.1f}% match)")
            print(f"  • Title       : {paper.get('title')}")
            print(f"  • Paper ID    : {paper.get('paperId')}")
            print(f"  • Authors     : {paper.get('authors')}")
            print(f"  • Year        : {paper.get('year')}")
            print(f"  • URL         : {paper.get('url')}")
            print(f"  • Abstract    : {paper.get('abstract')[:250]}...")
            print("-" * 75)


if __name__ == "__main__":
    main()
