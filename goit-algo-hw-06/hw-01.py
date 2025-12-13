import networkx as nx
import matplotlib.pyplot as plt

# Transport network model: vertices — stops (A..I), edges — roads between them,
# weight — conditional distance/travel time.

# Create a graph with nodes and edges
G = nx.Graph()
G.add_nodes_from(["A", "B", "C", "D", "E", "F", "G", "H", "I"])
G.add_edge("A", "B", weight=4)
G.add_edge("A", "H", weight=8)
G.add_edge("B", "C", weight=8)
G.add_edge("B", "H", weight=11)
G.add_edge("C", "D", weight=7)
G.add_edge("C", "F", weight=4)
G.add_edge("C", "I", weight=2)
G.add_edge("D", "E", weight=9)
G.add_edge("D", "F", weight=14)
G.add_edge("E", "F", weight=10)
G.add_edge("F", "G", weight=2)
G.add_edge("G", "H", weight=1)
G.add_edge("G", "I", weight=6)
G.add_edge("H", "I", weight=7)

# Show the graph properties
print("Graph nodes : ")
print(G.nodes)
print("Graph edges : ")
print(G.edges)
print(f"Amount of nodes : {G.number_of_nodes()}")
print(f"Amount of edges : {G.number_of_edges()}")
print("C neighbors : ")
print(list(G.neighbors("C")))

# Degree of vertices (number of connections of each vertex)
degrees = dict(G.degree())
print("Node's degree:")
for node in sorted(degrees):
    print(f"  {node}: {degrees[node]}")

# Brief statistics on degrees
deg_values = list(degrees.values())
print(f"Min. degree: {min(deg_values)}")
print(f"Max. degree: {max(deg_values)}")
print(f"agv. degree: {sum(deg_values) / len(deg_values):.2f}")

# Show the betweenness centrality
betweenness_centrality = nx.betweenness_centrality(G) 
print(F"Betweenness centrality : {betweenness_centrality}")

# Find the shortest path from node A to node E
path = nx.shortest_path(G, "A", "E", weight="weight")
print(f"Shortest path : {path}")
# Show the length of path
short_length = nx.shortest_path_length(G, "A", "E", weight="weight")
print(f"Shortest path length: {short_length}")
# Show the all length of path
all_distances = dict(nx.all_pairs_dijkstra_path_length(G, weight="weight"))
print(f"The distance from A to E : {all_distances['A']['E']}")
# Show the all path
all_paths = dict(nx.all_pairs_dijkstra_path(G, weight="weight"))
print(f"The path from A to E: {all_paths['A']['E']}")

# Create a list of edges in the shortest path
path_edges = list(zip(path, path[1:]))

# Create a list of all edges, and assign colors based on whether they are in the shortest path or not
edge_colors = [
    "red" if edge in path_edges or tuple(reversed(edge)) in path_edges else "black"
    for edge in G.edges()
]

# Visualize the graph
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos)
nx.draw_networkx_edges(G, pos, edge_color=edge_colors)
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edge_labels(
    G, pos, edge_labels={(u, v): d["weight"] for u, v, d in G.edges(data=True)}
)

plt.show()