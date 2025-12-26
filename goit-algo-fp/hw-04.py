import uuid

import networkx as nx
import matplotlib.pyplot as plt

import heapq


class Node:
    def __init__(self, key, color="skyblue"):
        self.left = None
        self.right = None
        self.val = key
        self.color = color # Додатковий аргумент для зберігання кольору вузла
        self.id = str(uuid.uuid4()) # Унікальний ідентифікатор для кожного вузла

def add_edges(graph, node, pos, x=0, y=0, layer=1):
    if node is not None:
        graph.add_node(node.id, color=node.color, label=node.val) # Використання id та збереження значення вузла
        if node.left:
            graph.add_edge(node.id, node.left.id)
            l = x - 1 / 2 ** layer
            pos[node.left.id] = (l, y - 1)
            l = add_edges(graph, node.left, pos, x=l, y=y - 1, layer=layer + 1)
        if node.right:
            graph.add_edge(node.id, node.right.id)
            r = x + 1 / 2 ** layer
            pos[node.right.id] = (r, y - 1)
            r = add_edges(graph, node.right, pos, x=r, y=y - 1, layer=layer + 1)
    return graph

def draw_tree(tree_root):
    tree = nx.DiGraph()
    pos = {tree_root.id: (0, 0)}
    tree = add_edges(tree, tree_root, pos)

    colors = [node[1]['color'] for node in tree.nodes(data=True)]
    labels = {node[0]: node[1]['label'] for node in tree.nodes(data=True)} # Використовуйте значення вузла для міток

    plt.figure(figsize=(8, 5))
    nx.draw(tree, pos=pos, labels=labels, arrows=False, node_size=2500, node_color=colors)
    plt.show()

def heap_to_tree(heap: list[int | float]) -> Node | None:
    """
    Будує бінарне дерево Node з масиву купи (0-індексація як у heapq).
    Для елемента з індексом i:
      left = 2*i + 1
      right = 2*i + 2
    """
    if not heap:
        return None

    # 1) Створюємо вузли для кожного елемента купи
    nodes = [Node(value) for value in heap]

    # 2) Прив'язуємо дітей за індексами
    n = len(nodes)
    for i in range(n):
        left_i = 2 * i + 1
        right_i = 2 * i + 2

        if left_i < n:
            nodes[i].left = nodes[left_i]
        if right_i < n:
            nodes[i].right = nodes[right_i]

    # 3) Корінь — нульовий елемент масиву
    return nodes[0]


def visualize_heap(heap: list[int | float], *, ensure_heap: bool = True) -> None:
    """
    * - передача параметрів за іменем
    Візуалізує бінарну купу:
    - ensure_heap=True: гарантує, що список є купою (виконає heapify на копії).
      Якщо коректна купа (після heapq.heapify / heappush), можна False.
    """
    if not heap:
        print("Купа порожня — нічого візуалізувати.")
        return

    data = heap[:]  # копія, щоб не псувати оригінал

    # (Опційно) перетворюємо список у валідну min-heap
    if ensure_heap:
        heapq.heapify(data)

    root = heap_to_tree(data)
    if root is None:
        print("Не вдалося побудувати дерево з купи.")
        return

    # Малюємо дерево
    draw_tree(root)

if __name__ == "__main__":
    arr = [10, 3, 7, 1, 9, 4, 8]
    visualize_heap(arr, ensure_heap=True)   # зробить heapify і намалює min-heap
