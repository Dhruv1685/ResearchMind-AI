import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Global cache for the SentenceTransformer model to prevent re-loading on every call
_model = None


def get_model():
    """
    Lazy-loader for the SentenceTransformer model.
    Loads 'all-MiniLM-L6-v2' once and reuses it for efficiency.
    """
    global _model
    if _model is None:
        print("\n[+] Loading Sentence Transformer model ('all-MiniLM-L6-v2')...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generate_paper_embeddings(papers):
    """
    Combines the title and abstract of each paper into a single text block
    and generates numerical embedding vectors (384 dimensions) using Sentence-BERT.

    Parameters:
        papers (list): List of paper dictionaries from Module 1.

    Returns:
        np.ndarray: Matrix of embeddings of shape (N, 384).
    """
    if not papers:
        return np.array([])

    text_list = []
    for paper in papers:
        title = paper.get("title", "")
        abstract = paper.get("abstract", "")

        # Handle missing or default abstract gracefully
        if not abstract or abstract == "No abstract available for this paper.":
            combined_text = f"Title: {title}."
        else:
            combined_text = f"Title: {title}. Abstract: {abstract}"

        text_list.append(combined_text)

    # Get model and encode texts into numerical dense vectors
    model = get_model()
    print(f"[+] Generating semantic embeddings for {len(papers)} papers...")
    embeddings = model.encode(text_list, show_progress_bar=False)
    return embeddings


def recommend_similar_papers(papers, target_index, top_n=3):
    """
    Calculates cosine similarity between the selected target paper and all other papers,
    and returns top N recommendations sorted by similarity score.

    Parameters:
        papers (list): List of paper dictionaries.
        target_index (int): 0-based index of the selected paper.
        top_n (int): Number of recommended papers to return (default 3).

    Returns:
        list: List of tuples (paper_dict, similarity_score).
    """
    if not papers or target_index < 0 or target_index >= len(papers):
        return []

    # 1. Generate embeddings for all papers
    embeddings = generate_paper_embeddings(papers)
    if len(embeddings) == 0:
        return []

    # 2. Extract embedding of selected target paper and reshape for sklearn (1, 384)
    target_embedding = embeddings[target_index].reshape(1, -1)

    # 3. Compute cosine similarity scores between target paper and all papers
    similarity_scores = cosine_similarity(target_embedding, embeddings)[0]

    # 4. Pair papers with their similarity scores (excluding the target paper itself)
    recommendations = []
    for idx, score in enumerate(similarity_scores):
        if idx != target_index:  # Do not recommend the selected paper to itself
            recommendations.append((papers[idx], float(score)))

    # 5. Sort recommendations by similarity score in descending order (highest score first)
    recommendations.sort(key=lambda item: item[1], reverse=True)

    # 6. Return top N recommendations
    return recommendations[:top_n]
