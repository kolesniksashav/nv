import heapq
from typing import List


def min_cost_to_connect_cables(cables: List[int]) -> int:
    """
    Обчислює мінімальну загальну вартість з'єднання кабелів.
    Використовує мін-купу (heapq).
    """
    if not cables:
        print("Немає кабелів для з'єднання.")
        return 0

    if len(cables) == 1:
        print("Лише один кабель — вартість 0.")
        return 0

    # Створюємо мін-купу
    heap = cables[:]
    heapq.heapify(heap)

    total_cost = 0
    step = 1

    print("Початкові довжини кабелів:", heap)
    print("-" * 50)

    while len(heap) > 1:
        first = heapq.heappop(heap)
        second = heapq.heappop(heap)

        cost = first + second
        total_cost += cost

        print(f"Крок {step}: з'єднуємо {first} + {second} = {cost}")
        print(f"  Поточна сумарна вартість: {total_cost}")

        heapq.heappush(heap, cost)
        print(f"  Купа після з'єднання: {heap}")
        print("-" * 50)

        step += 1

    print(f"Загальна мінімальна вартість: {total_cost}")
    return total_cost

cables = [4, 3, 2, 6]
min_cost_to_connect_cables(cables)