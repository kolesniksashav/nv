import networkx as nx
from collections import deque

# =========================================
# DFS і BFS для знаходження шляхів
# =========================================
# Важливо:
# - Ми будуємо "дерево обходу" (search tree) для DFS та BFS
# - Далі відновлюємо шлях A -> v по батьківських посиланнях (parent)
# - Для стабільного результату фіксуємо порядок сусідів через sorted()
#   (інакше порядок у NetworkX може відрізнятися від запуску до запуску)


def build_graph() -> nx.Graph:
    # Створює граф з першого завдання (вузли та ребра з вагами).
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

    return G

def dfs_parents_iterative(graph: nx.Graph, start: str) -> tuple[list[str], dict]:
    """
    Ітеративний DFS.
    Повертає:
      - order: порядок відвідування вершин
      - parent: батьківські посилання (дерево DFS)
    """
    visited = set()
    parent = {start: None}
    order = []

    stack = [start]
    while stack:
        v = stack.pop()
        if v in visited:
            continue

        visited.add(v)
        order.append(v)

        # Щоб обхід був стабільний:
        # 1) сортуємо сусідів за зростанням
        # 2) кладемо в стек у зворотному порядку, бо стек LIFO
        neighbors = sorted(graph.neighbors(v), reverse=True)
        for nb in neighbors:
            if nb not in visited and nb not in parent:
                parent[nb] = v
            stack.append(nb)

    return order, parent

def bfs_parents_iterative(graph: nx.Graph, start: str) -> tuple[list[str], dict]:
    """
    Ітеративний BFS.
    Повертає:
      - order: порядок відвідування вершин
      - parent: батьківські посилання (дерево BFS)
    """
    visited = set([start])
    parent = {start: None}
    order = []

    q = deque([start])
    while q:
        v = q.popleft()
        order.append(v)

        # Сусіди в стабільному порядку
        for nb in sorted(graph.neighbors(v)):
            if nb in visited:
                continue
            visited.add(nb)
            parent[nb] = v
            q.append(nb)

    return order, parent

# Виведення результатів
def reconstruct_path(parent: dict, start: str, goal: str) -> list[str] | None:
    # Відновлює шлях start -> goal за словником parent. Повертає список вершин.
    if goal not in parent:
        return None

    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()

    # Якщо шлях не починається зі start — значить goal не досяжна зі start
    if not path or path[0] != start:
        return None
    return path

def format_path(path: list[str] | None) -> str:
    """Красивий друк шляху."""
    if path is None:
        return "-"
    return " -> ".join(path)


def print_paths_table(start: str, nodes: list[str], dfs_parent: dict, bfs_parent: dict) -> None:
    # Друкує таблицю у 3 колонки однакової ширини:
    # Шлях (цільова вершина); DFS; BFS
    rows = []
    for goal in nodes:
        dfs_path = format_path(reconstruct_path(dfs_parent, start, goal))
        bfs_path = format_path(reconstruct_path(bfs_parent, start, goal))
        rows.append((goal, dfs_path, bfs_path))

    # Однакова ширина для ВСІХ колонок
    headers = ("Шлях", "DFS", "BFS")
    max_cell_len = max(
        *(len(x) for row in rows for x in row),
        *(len(h) for h in headers)
    )
    col_w = max_cell_len + 2  # трохи “повітря”

    def cell(s: str) -> str:
        return f"{s:<{col_w}}"

    print("\Шляхи з A (DFS tree vs BFS tree):")
    print(cell(headers[0]) + cell(headers[1]) + cell(headers[2]))
    print("-" * (col_w * 3))

    for goal, dfs_path, bfs_path in rows:
        print(cell(goal) + cell(dfs_path) + cell(bfs_path))


def main() -> None:
    G = build_graph()

    start = "A"
    dfs_order, dfs_parent = dfs_parents_iterative(G, start)
    bfs_order, bfs_parent = bfs_parents_iterative(G, start)

    print("DFS послідовність:", dfs_order)
    print("BFS послідовність:", bfs_order)

    nodes_sorted = sorted(G.nodes())
    print_paths_table(start, nodes_sorted, dfs_parent, bfs_parent)

    # Коротке пояснення прямо в консолі (детальніше — у README)
    print("\nПояснення коротко:")
    print("- BFS будує шляхи з мінімальною кількістю ребер (найменше 'кроків').")
    print("- DFS йде вглиб настільки, наскільки дозволяють ребра, тому шлях часто не мінімальний.")
    print("- Різниця в шляхах зумовлена різною стратегією обходу + порядком сусідів (sorted).")


if __name__ == "__main__":
    main()
