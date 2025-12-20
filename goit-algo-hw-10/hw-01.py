from pulp import LpProblem, LpVariable, LpMaximize, lpSum, LpStatus, value


def solve_production():
    # 1) Модель (максимізація)
    model = LpProblem("Drink_Production_Optimization", LpMaximize)

    # 2) Змінні (цілі, невід’ємні)
    L = LpVariable("Lemonade", lowBound=0, cat="Integer")
    J = LpVariable("FruitJuice", lowBound=0, cat="Integer")

    # 3) Цільова функція: максимізувати загальну кількість напоїв
    model += L + J, "Total_Produced_Drinks"

    # 4) Обмеження ресурсів
    # Вода:
    model += 2 * L + 1 * J <= 100, "Water"

    # Цукор:
    model += 1 * L <= 50, "Sugar"

    # Лимонний сік:
    model += 1 * L <= 30, "Lemon_Juice"

    # Фруктове пюре:
    model += 2 * J <= 40, "Fruit_Puree"

    # 5) Розв'язання
    model.solve()

    # 6) Результати
    status = LpStatus[model.status]
    lemonade = int(value(L))
    juice = int(value(J))
    total = int(value(L + J))

    return status, lemonade, juice, total


if __name__ == "__main__":
    status, lemonade, juice, total = solve_production()

    print("Статус розв'язання:", status)
    print("Лимонад (L):", lemonade)
    print("Фруктовий сік (J):", juice)
    print("Загальна кількість:", total)
