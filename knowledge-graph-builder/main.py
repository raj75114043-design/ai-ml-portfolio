from src.builder import build, to_cypher

g, review = build()
print(f"Graph built: {g.number_of_nodes()} nodes, {g.number_of_edges()} relationships")
print("Entity resolution:")
for u, v, d in g.edges(data=True):
    if d["type"] == "SUPPLIED_BY":
        print(f"  {u} -> {v} ({g.nodes[v]['name']}), confidence {d['confidence']}")
print(f"Low-confidence matches for manual review: {review or 'none'}")

print("\nMulti-hop query: SITE-101 -> Activity -> Material -> Vendor")
for act in g.successors("SITE-101"):
    for mat in g.successors(act):
        for ven in g.successors(mat):
            print(f"  SITE-101 -> {g.nodes[act]['name']} [{g.nodes[act]['status']}] -> "
                  f"{g.nodes[mat]['name']} -> {g.nodes[ven]['name']}")

print("\nFirst Cypher statements for Neo4j:")
for s in to_cypher(g)[:3]:
    print("  " + s)
