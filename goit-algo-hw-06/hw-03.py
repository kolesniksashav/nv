import math
import networkx as nx


# === 1) Граф з вагами ребер ===
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


# === 2) Дейкстра (відстані + "батьки" для відновлення шляху) ===
def dijkstra_with_paths(graph: nx.Graph, start):
    # distances[v] — найкоротша відстань від start до v
    distances = {node: math.inf for node in graph.nodes}
    distances[start] = 0

    # previous[v] — попередня вершина на найкоротшому шляху до v
    previous = {node: None for node in graph.nodes}

    # множина невідвіданих вершин
    unvisited = set(graph.nodes)

    while unvisited:
        # вибираємо вершину з мінімальною поточною відстанню
        current = min(unvisited, key=lambda node: distances[node])

        # якщо "найкраще" з того, що лишилось — нескінченність, далі шляхів немає
        if distances[current] == math.inf:
            break

        # релаксація ребер
        for neighbor in graph.neighbors(current):
            weight = graph[current][neighbor].get("weight", 1)
            new_distance = distances[current] + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current

        unvisited.remove(current)

    return distances, previous


def restore_path(previous, start, end):
    # Відновлює шлях start -> end за словником previous.
    path = []
    current = end

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()
    return path if path and path[0] == start else None


def all_pairs_shortest_paths(graph: nx.Graph):
    # Запускає Дейкстру з кожної вершини: all-pairs shortest paths.
    all_distances = {}
    all_paths = {}

    for start in graph.nodes:
        distances, previous = dijkstra_with_paths(graph, start)
        all_distances[start] = distances
        all_paths[start] = {}

        for end in graph.nodes:
            all_paths[start][end] = restore_path(previous, start, end)

    return all_distances, all_paths


# === 3) Вивід результатів для всіх пар вершин ===
distances, paths = all_pairs_shortest_paths(G)

for start in sorted(G.nodes):
    print(f"\nНайкоротші шляхи з вершини {start}:")
    for end in sorted(G.nodes):
        dist = distances[start][end]
        path = paths[start][end]

        if dist == math.inf or path is None:
            print(f"{start} → {end}: немає шляху")
        else:
            print(f"{start} → {end}: distance = {dist}, path = {path}")
