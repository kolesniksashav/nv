import uuid
import heapq
from collections import deque
from typing import Dict, List, Tuple, Optional

import networkx as nx
import matplotlib.pyplot as plt


class Node:
    def __init__(self, key, color="#6E6E6E"):
        self.left: Optional["Node"] = None
        self.right: Optional["Node"] = None
        self.val = key
        # Колір вузла (HEX #RRGGBB). За замовчуванням темний (ще не відвіданий)
        self.color = color
        # Унікальний ідентифікатор вузла для networkx
        self.id = str(uuid.uuid4())


def add_edges(graph: nx.DiGraph, node: Optional[Node], pos: Dict[str, Tuple[float, float]], x=0, y=0, layer=1):
    """
    Рекурсивно додає вузли/ребра у networkx-граф для ВІЗУАЛІЗАЦІЇ.
    ВАЖЛИВО: це НЕ DFS/BFS обхід (вимога "без рекурсії" стосується саме обходів).
    """
    if node is not None:
        graph.add_node(node.id, color=node.color, label=node.val)

        if node.left:
            graph.add_edge(node.id, node.left.id)
            lx = x - 1 / (2 ** layer)
            pos[node.left.id] = (lx, y - 1)
            add_edges(graph, node.left, pos, x=lx, y=y - 1, layer=layer + 1)

        if node.right:
            graph.add_edge(node.id, node.right.id)
            rx = x + 1 / (2 ** layer)
            pos[node.right.id] = (rx, y - 1)
            add_edges(graph, node.right, pos, x=rx, y=y - 1, layer=layer + 1)

    return graph


def build_nx_tree(tree_root: Node) -> Tuple[nx.DiGraph, Dict[str, Tuple[float, float]], Dict[str, str]]:
    """
    Будує networkx-граф дерева 1 раз (структуру + позиції + labels).
    Далі для анімації ми лише оновлюємо node['color'].
    """
    tree = nx.DiGraph()
    pos = {tree_root.id: (0, 0)}
    tree = add_edges(tree, tree_root, pos)

    labels = {node_id: str(data["label"]) for node_id, data in tree.nodes(data=True)}
    return tree, pos, labels


def draw_tree_frame(tree: nx.DiGraph, pos: Dict[str, Tuple[float, float]], labels: Dict[str, str], title: str):
    """
    Малює один кадр (frame) для анімації. НЕ викликає plt.show().
    """
    plt.clf()
    colors = [data.get("color", "#6E6E6E") for _, data in tree.nodes(data=True)]
    nx.draw(
        tree,
        pos=pos,
        labels=labels,
        arrows=False,
        node_size=2500,
        node_color=colors,
        font_size=12,
        font_weight="bold",
    )
    plt.title(title)
    plt.axis("off")


# =========================
# купа -> дерево
# =========================

def heap_to_tree(heap: List[int | float]) -> Optional[Node]:
    """
    Будує бінарне дерево Node з масиву купи (0-індексація як у heapq).
    Для елемента з індексом i:
      left = 2*i + 1
      right = 2*i + 2
    """
    if not heap:
        return None

    nodes = [Node(value) for value in heap]
    n = len(nodes)

    for i in range(n):
        li = 2 * i + 1
        ri = 2 * i + 2
        if li < n:
            nodes[i].left = nodes[li]
        if ri < n:
            nodes[i].right = nodes[ri]

    return nodes[0]


def visualize_heap(heap: List[int | float], *, ensure_heap: bool = True) -> Optional[Node]:
    """
    Візуалізує купу як дерево. Повертає root (щоб потім можна було зробити DFS/BFS).
    ensure_heap=True -> heapify на копії, щоб гарантовано отримати min-heap.
    """
    if not heap:
        print("Купа порожня — нічого візуалізувати.")
        return None

    data = heap[:]
    if ensure_heap:
        heapq.heapify(data)

    root = heap_to_tree(data)
    if root is None:
        print("Не вдалося побудувати дерево з купи.")
        return None

    tree, pos, labels = build_nx_tree(root)
    plt.figure(figsize=(9, 6))
    draw_tree_frame(tree, pos, labels, title="Бінарна купа як дерево (перед обходом)")
    plt.show()
    return root


# =========================
# DFS/BFS (без рекурсії) + градієнт кольорів
# =========================

def hex_gradient(start_hex: str, end_hex: str, steps: int) -> List[str]:
    """
    Генерує steps HEX-кольорів від темного до світлого (наприклад #0B1B3A -> #CFEFFF).
    """
    def hex_to_rgb(h: str) -> Tuple[int, int, int]:
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def rgb_to_hex(r: int, g: int, b: int) -> str:
        return f"#{r:02X}{g:02X}{b:02X}"

    if steps <= 0:
        return []
    if steps == 1:
        return [end_hex.upper()]

    sr, sg, sb = hex_to_rgb(start_hex)
    er, eg, eb = hex_to_rgb(end_hex)

    out: List[str] = []
    for i in range(steps):
        t = i / (steps - 1)
        r = round(sr + (er - sr) * t)
        g = round(sg + (eg - sg) * t)
        b = round(sb + (eb - sb) * t)
        out.append(rgb_to_hex(r, g, b))
    return out


def dfs_iterative(root: Optional[Node]) -> List[Node]:
    """
    DFS у глибину (preorder): root -> left -> right
    ВИМОГА: використовуємо стек (list), НЕ рекурсію.
    """
    if root is None:
        return []

    order: List[Node] = []
    stack: List[Node] = [root]

    while stack:
        node = stack.pop()
        order.append(node)

        # Щоб обхід був стабільним: "ліво першим"
        # Тому в стек кладемо спочатку right, потім left
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)

    return order


def bfs_iterative(root: Optional[Node]) -> List[Node]:
    """
    BFS у ширину: рівень за рівнем
    ВИМОГА: використовуємо чергу (deque), НЕ рекурсію.
    """
    if root is None:
        return []

    order: List[Node] = []
    q: deque[Node] = deque([root])

    while q:
        node = q.popleft()
        order.append(node)

        if node.left is not None:
            q.append(node.left)
        if node.right is not None:
            q.append(node.right)

    return order


def visualize_traversal(root: Node, traversal: str, delay: float = 0.6):
    """
    Покрокова візуалізація DFS/BFS.
    - traversal: "DFS" або "BFS"
    - delay: пауза між кроками (сек)
    """
    traversal = traversal.upper().strip()
    if traversal not in {"DFS", "BFS"}:
        raise ValueError("traversal має бути 'DFS' або 'BFS'")

    # Отримуємо порядок відвідування без рекурсії (стек/черга)
    visit_order = dfs_iterative(root) if traversal == "DFS" else bfs_iterative(root)

    # Градієнт: від темного до світлого
    colors = hex_gradient("#3A6EA5", "#E6F4FF", steps=len(visit_order))

    # Будуємо структуру дерева для малювання один раз
    tree, pos, labels = build_nx_tree(root)

    # Скидаємо всі вузли в "темний" (не відвідані)
    for node_id in tree.nodes:
        tree.nodes[node_id]["color"] = "#6E6E6E"

    plt.figure(figsize=(9, 6))
    plt.ion()  # інтерактивний режим (щоб кадри мінялися без блокування)

    # Малюємо кроки
    for i, node in enumerate(visit_order, start=1):
        tree.nodes[node.id]["color"] = colors[i - 1]
        draw_tree_frame(tree, pos, labels, title=f"{traversal}: крок {i}/{len(visit_order)}")
        plt.pause(delay)

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    # Приклад: будуємо купу і дерево з неї
    arr = [10, 3, 7, 1, 9, 4, 8, 16, 2, 12, 6]
    root = visualize_heap(arr, ensure_heap=True)

    # Якщо дерево побудувалось — візуалізуємо обходи
    if root is not None:
        visualize_traversal(root, "DFS", delay=0.7)
        visualize_traversal(root, "BFS", delay=0.7)
