import re
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer

STOP = set("a an the is are was were be to of in on for and or with my me i it this that what how do does "
           "can when why where which who our we you your not have has must should many much long".split())


def stem(token):
    """Light suffix stripping so 'averaged', 'averaging' and 'average' match."""
    for suffix in ("ing", "ed", "es", "s", "e"):
        if token.endswith(suffix) and len(token) > len(suffix) + 3:
            return token[: -len(suffix)]
    return token


def tokenize(text):
    return [stem(t) for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP]


class HybridRetriever:
    """BM25 + character n-gram TF-IDF fused with weighted Reciprocal Rank Fusion."""

    def __init__(self, chunks, dense_weight=0.6, sparse_weight=0.4):
        self.chunks = chunks
        texts = [c["text"] for c in chunks]
        self.bm25 = BM25Okapi([tokenize(t) for t in texts])
        self.vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        self.matrix = self.vec.fit_transform(texts)
        self.weights = (dense_weight, sparse_weight)

    def _rank(self, scores):
        return list(np.argsort(scores)[::-1])

    def search(self, query, k=3, rrf_k=60):
        sparse = self.bm25.get_scores(tokenize(query))
        dense = (self.matrix @ self.vec.transform([query]).T).toarray().ravel()
        fused = {}
        for weight, ranking in ((self.weights[0], self._rank(dense)), (self.weights[1], self._rank(sparse))):
            for rank, idx in enumerate(ranking):
                fused[idx] = fused.get(idx, 0.0) + weight / (rrf_k + rank + 1)
        order = sorted(fused, key=fused.get, reverse=True)[:k]
        return [dict(self.chunks[i], bm25=round(float(sparse[i]), 2)) for i in order]
