import numpy as np


def recall_at_k(retrieved, relevant, k):
    return len(set(retrieved[:k]) & set(relevant)) / len(relevant)


def mrr(retrieved, relevant):
    for i, d in enumerate(retrieved):
        if d in relevant:
            return 1 / (i + 1)
    return 0.0


def evaluate(retriever, eval_set, k=3):
    rec, rr = [], []
    for item in eval_set:
        res = retriever.search(item["query"], 10)
        rec.append(recall_at_k(res, item["relevant"], k))
        rr.append(mrr(res, item["relevant"]))
    return {"recall@k": round(float(np.mean(rec)), 3), "mrr": round(float(np.mean(rr)), 3)}
