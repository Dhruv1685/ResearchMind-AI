"""
ResearchMind AI — Main Application Entry Point
Integrates Module 1 (Paper Search) & Module 2 (ML Recommendation)
"""

from backend.paper_search import search_papers, display_papers
from backend.paper_recommender import recommend_similar_papers


def main():
    print("=" * 70)
    print(" ResearchMind AI — Intelligent Research Paper Search & Recommender")
    print("=" * 70)

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
    # MODULE 2: ML-BASED RECOMMENDATION
    # -------------------------------------------------------------
    if len(papers) < 2:
        print("\n[!] Need at least 2 papers to perform recommendation.")
        return

    print("\n" + "=" * 70)
    print(" MODULE 2: ML-BASED PAPER RECOMMENDATION")
    print("=" * 70)

    # Ask user to pick a paper number
    while True:
        try:
            choice = input(f"\nSelect a paper number (1 to {len(papers)}) to find recommendations: ").strip()
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

    # Get top 3 recommendations
    top_n = min(3, len(papers) - 1)
    recommendations = recommend_similar_papers(papers, target_index, top_n=top_n)

    # Display recommendations
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
