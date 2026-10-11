import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer


def tokenize(text: str) -> list[str]:
    return [t.strip(".,?!").lower() for t in text.split()]


class SparseRetriever:
    """BM25 keyword retrieval — strong on error codes, IDs and acronyms."""
    def __init__(self, chunks):
        self.chunks = chunks
        self.bm25 = BM25Okapi([tokenize(c["text"]) for c in chunks])

    def search(self, query, k):
        scores = self.bm25.get_scores(tokenize(query))
        return [self.chunks[i]["id"] for i in np.argsort(scores)[::-1][:k]]


class DenseRetriever:
    """Semantic retrieval. Uses sentence-transformers when installed, otherwise a
    character n-gram TF-IDF fallback so the demo runs fully offline."""
    def __init__(self, chunks):
        self.chunks = chunks
        texts = [c["text"] for c in chunks]
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.matrix = self.model.encode(texts, normalize_embeddings=True)
            self.backend = "sentence-transformers"
        except Exception:
            self.model = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
            self.matrix = self.model.fit_transform(texts)
            self.backend = "tfidf-char-fallback"

    def search(self, query, k):
        if self.backend == "sentence-transformers":
            q = self.model.encode([query], normalize_embeddings=True)
            scores = (self.matrix @ q.T).ravel()
        else:
            scores = (self.matrix @ self.model.transform([query]).T).toarray().ravel()
        return [self.chunks[i]["id"] for i in np.argsort(scores)[::-1][:k]]


def reciprocal_rank_fusion(rankings: dict, weights: dict, k: int = 60) -> list[str]:
    """Weighted RRF. Production configuration: 0.8 dense, 0.2 sparse."""
    fused = {}
    for name, ranking in rankings.items():
        for rank, doc_id in enumerate(ranking):
            fused[doc_id] = fused.get(doc_id, 0.0) + weights[name] / (k + rank + 1)
    return sorted(fused, key=fused.get, reverse=True)


class HybridRetriever:
    def __init__(self, chunks, dense_weight=0.8, sparse_weight=0.2):
        self.dense, self.sparse = DenseRetriever(chunks), SparseRetriever(chunks)
        self.weights = {"dense": dense_weight, "sparse": sparse_weight}

    def search(self, query, k=3, candidates=10):
        return reciprocal_rank_fusion(
            {"dense": self.dense.search(query, candidates), "sparse": self.sparse.search(query, candidates)},
            self.weights)[:k]
