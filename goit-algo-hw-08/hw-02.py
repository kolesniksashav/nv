import heapq
from typing import List


def merge_k_lists(lists: List[List[int]]) -> List[int]:
    """
    Зливає k відсортованих списків у один відсортований список через мін-купу.
    Складність: O(N log k)
    """
    heap = []
    result = []

    # 1) Заповнюємо купу першими елементами кожного непорожнього списку
    for list_index, arr in enumerate(lists):
        if arr:  # якщо список не порожній
            # (значення, індекс списку, індекс елемента в цьому списку)
            heapq.heappush(heap, (arr[0], list_index, 0))

    # 2) Поки купа не порожня — дістаємо мінімум і підкладаємо наступний елемент
    while heap:
        value, list_index, element_index = heapq.heappop(heap)
        result.append(value)

        next_index = element_index + 1
        if next_index < len(lists[list_index]):
            next_value = lists[list_index][next_index]
            heapq.heappush(heap, (next_value, list_index, next_index))

    return result


# --- Приклад з умови ---
lists = [[1, 4, 5], [1, 3, 4], [2, 6]]
merged_list = merge_k_lists(lists)
print("Відсортований список:", merged_list)
