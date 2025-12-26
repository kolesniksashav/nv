from __future__ import annotations

import heapq
from typing import Dict, List, Tuple, Optional

import networkx as nx
import matplotlib.pyplot as plt


Graph = Dict[str, Dict[str, float]]  # adjacency: {u: {v: weight, ...}, ...}

def visualize_graph(graph: dict) -> None:
    """
    Візуалізує зважений граф зі словника суміжності
    """
    G = nx.Graph()

    # Додаємо ребра
    for u, neighbors in graph.items():
        for v, w in neighbors.items():
            G.add_edge(u, v, weight=w)

    # Позиції вершин (spring layout — гарний універсальний варіант)
    pos = nx.spring_layout(G, seed=42)

    # Малюємо вершини та ребра
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=2000,
        node_color="lightblue",
        font_size=12,
        font_weight="bold",
        edge_color="gray",
    )

    # Підписи ваг ребер
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title("Зважений граф (для алгоритму Дейкстри)")
    plt.show()

def dijkstra_heap(graph: Graph, start: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """
    Алгоритм Дейкстри з використанням бінарної купи (heapq).
    Повертає:
      - distances: найкоротші відстані від start до кожної вершини
      - prev: попередник для відновлення найкоротшого шляху (дерево шляхів)
    Вимога: ваги ребер мають бути невід'ємні.
    """
    if start not in graph:
        raise ValueError(f"Стартової вершини '{start}' немає в графі")

    # 1) Ініціалізація
    distances: Dict[str, float] = {v: float("inf") for v in graph}
    prev: Dict[str, Optional[str]] = {v: None for v in graph}

    distances[start] = 0.0

    # 2) Мін-купа: (поточна_відстань, вершина)
    heap: List[Tuple[float, str]] = [(0.0, start)]

    # 3) Основний цикл
    while heap:
        # дістаємо вершину
        cur_dist, u = heapq.heappop(heap)

        # Якщо витягнули "застарілий" запис (є краща відстань) — пропускаємо
        # Відкидаємо гірший варіант, більшу відстань
        if cur_dist != distances[u]:
            continue

        # Перебір сусідів
        # Для кожної вершини отримуємо сусідню вершину і вагу ребра
        for v, w in graph[u].items():
            if w < 0:
                raise ValueError("Дейкстра не працює з від'ємними вагами ребер")

            new_dist = cur_dist + w # найкоротша відстань + вага
            if new_dist < distances[v]:
                distances[v] = new_dist # найкоротший шлях
                prev[v] = u # запам'ятовуємо вершину которкого шляху
                heapq.heappush(heap, (new_dist, v)) # зберігаємо в купу

    return distances, prev

def reconstruct_path(prev: Dict[str, Optional[str]], start: str, target: str) -> List[str]:
    """
    Відновлює шлях start -> target за словником prev.
    Якщо шлях не існує — повертає порожній список.
    """
    if start == target:
        return [start]

    path: List[str] = []
    cur: Optional[str] = target

    while cur is not None:
        path.append(cur)
        cur = prev[cur]

    path.reverse()

    # якщо шлях не починається зі start — значить вершина недосяжна
    if not path or path[0] != start:
        return []
    return path

def build_demo_graph() -> Graph:
    """
    Приклад зваженого неорієнтованого графа.
    Для неорієнтованого графа додаємо ребро в обидва боки.
    """
    graph: Graph = {
        "A": {"B": 4, "H": 8},
        "B": {"A": 4, "C": 8, "H": 11},
        "C": {"B": 8, "D": 7, "F": 4, "I": 2},
        "D": {"C": 7, "E": 9, "F": 14},
        "E": {"D": 9, "F": 10},
        "F": {"C": 4, "D": 14, "E": 10, "G": 2},
        "G": {"F": 2, "H": 1, "I": 6},
        "H": {"A": 8, "B": 11, "G": 1, "I": 7},
        "I": {"C": 2, "G": 6, "H": 7},
    }
    return graph

def main() -> None:
    graph = build_demo_graph()
    start = "A"
       
    distances, prev = dijkstra_heap(graph, start)

    print(f"Найкоротші відстані від '{start}':")
    for v in sorted(distances):
        dist = distances[v]
        if dist == float("inf"):
            print(f"  {start} -> {v}: недосяжно")
        else:
            path = reconstruct_path(prev, start, v)
            path_str = " -> ".join(path) if path else "—"
            print(f"  {start} -> {v}: {dist:.0f} | шлях: {path_str}")

    visualize_graph(graph)  


if __name__ == "__main__":
    main()
