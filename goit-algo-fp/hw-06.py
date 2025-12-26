from __future__ import annotations
from typing import Dict, List, Tuple


Items = Dict[str, Dict[str, int]]

def greedy_algorithm(items: Items, budget: int) -> Tuple[List[str], int, int]:
    """
    Жадібний алгоритм:
    - сортує страви за співвідношенням calories/cost (спадання)
    - додає, поки не перевищимо бюджет
    Greedy: беремо за найбільшим calories / cost, доки вистачає бюджету.
    Greedy швидкий і простий, але не гарантує оптимум: 
       локально вигідні страви (за ratio) можуть “забити” бюджет так, 
       що глобально калорій вийде менше.
    Повертає: (список_страв, сумарна_вартість, сумарні_калорії)
    """
    if budget < 0:
        raise ValueError("budget має бути >= 0")

    # (назва, cost, calories, ratio)
    ranked = []
    for name, info in items.items():
        cost = int(info["cost"])
        calories = int(info["calories"])
        if cost <= 0:
            # захист від ділення на 0/некоректних даних
            continue
        ranked.append((name, cost, calories, calories / cost))

    ranked.sort(key=lambda x: x[3], reverse=True)

    chosen: List[str] = []
    total_cost = 0
    total_calories = 0

    for name, cost, calories, _ in ranked:
        if total_cost + cost <= budget:
            chosen.append(name)
            total_cost += cost
            total_calories += calories

    return chosen, total_cost, total_calories


def dynamic_programming(items: Items, budget: int) -> Tuple[List[str], int, int]:
    """
    Динамічне програмування (0/1 knapsack):
    dp[b] = максимум калорій при бюджеті b
    + відновлення вибраних страв (backtracking)
    DP: гарантує оптимум за калоріями при заданому бюджеті.
    DP повільніший (по часу/пам’яті), але завжди знаходить оптимальний набір для 0/1 задачі.
    Повертає: (список_страв, сумарна_вартість, сумарні_калорії)
    """
    if budget < 0:
        raise ValueError("budget має бути >= 0")

    names = list(items.keys())
    costs = [int(items[n]["cost"]) for n in names]
    calories = [int(items[n]["calories"]) for n in names]
    n = len(names)

    # dp[i][b] — максимум калорій, використовуючи перші i страв при бюджеті b
    dp = [[0] * (budget + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        c = costs[i - 1]
        cal = calories[i - 1]
        for b in range(budget + 1):
            # не беремо i-ту страву
            dp[i][b] = dp[i - 1][b]
            # беремо i-ту страву (якщо влазить у бюджет)
            if c <= b:
                dp[i][b] = max(dp[i][b], dp[i - 1][b - c] + cal)

    # Відновлюємо набір страв
    chosen: List[str] = []
    b = budget
    for i in range(n, 0, -1):
        if dp[i][b] != dp[i - 1][b]:
            chosen.append(names[i - 1])
            b -= costs[i - 1]

    chosen.reverse()

    total_cost = sum(items[name]["cost"] for name in chosen)
    total_calories = sum(items[name]["calories"] for name in chosen)

    return chosen, total_cost, total_calories


def main() -> None:
    # словник їжі
    items = {
        "pizza": {"cost": 50, "calories": 300},
        "hamburger": {"cost": 40, "calories": 250},
        "hot-dog": {"cost": 30, "calories": 200},
        "pepsi": {"cost": 10, "calories": 100},
        "cola": {"cost": 15, "calories": 220},
        "potato": {"cost": 25, "calories": 350},
    }

    budget = 100

    g_items, g_cost, g_cal = greedy_algorithm(items, budget)
    d_items, d_cost, d_cal = dynamic_programming(items, budget)

    print(f"Budget = {budget}\n")

    print("Greedy:")
    print("  chosen:", g_items)
    print("  cost  :", g_cost)
    print("  cal   :", g_cal, "\n")

    print("Dynamic programming:")
    print("  chosen:", d_items)
    print("  cost  :", d_cost)
    print("  cal   :", d_cal)


if __name__ == "__main__":
    main()
