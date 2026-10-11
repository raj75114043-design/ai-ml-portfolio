import sys
from src.graph import build_graph

if __name__ == "__main__":
    app = build_graph()
    queries = sys.argv[1:] or ["Why is SITE-101 down?", "What is the status of SITE-102?", "Why is SITE-103 delayed?"]
    for q in queries:
        result = app.invoke({"query": q})
        print(f"Q: {q}\nA: {result['answer']}\n")
