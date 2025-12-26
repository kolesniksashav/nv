import random
import matplotlib
matplotlib.use("TkAgg")  # Гарантує відкриття графіка в окремому вікні

import matplotlib.pyplot as plt


# ====== АНАЛІТИЧНІ ЙМОВІРНОСТІ ======
ANALYTICAL_PROBABILITIES = {
    2: 1 / 36,
    3: 2 / 36,
    4: 3 / 36,
    5: 4 / 36,
    6: 5 / 36,
    7: 6 / 36,
    8: 5 / 36,
    9: 4 / 36,
    10: 3 / 36,
    11: 2 / 36,
    12: 1 / 36,
}


def monte_carlo_dice_simulation(rolls: int = 1_000_000) -> dict[int, float]:
    # Симуляція кидків двох кубиків методом Монте-Карло.
    # Повертає ймовірності для сум від 2 до 12.

    # Створюємо порожній словник, для кожного i від 2 до 12 створити пару i: 0
    counts = {i: 0 for i in range(2, 13)}

    for _ in range(rolls):
        dice_sum = random.randint(1, 6) + random.randint(1, 6)
        counts[dice_sum] += 1 # рахуємо скільки разів кожна сума з’явилась
    
    # Перетворюємо кількість появ кожної суми на ймовірність.
    # k — key, сума кубиків (від 2 до 12)
    # v — value, скільки разів ця сума випала
    # rolls — загальна кількість симуляцій

    probabilities = {k: v / rolls for k, v in counts.items()}
    return probabilities


def print_probability_table(mc_probs: dict[int, float]) -> None:
    # Виводить таблицю порівняння: Монте-Карло vs Аналітичні значення

    print("\nТаблиця ймовірностей (Монте-Карло vs Аналітика)")
    print("-" * 60)
    print(f"{'Сума':<6}{'Monte-Carlo':<18}{'Аналітична':<18}{'Різниця'}")
    print("-" * 60)

    for s in range(2, 13):
        mc = mc_probs[s]
        an = ANALYTICAL_PROBABILITIES[s]
        diff = abs(mc - an)
        print(f"{s:<6}{mc:<18.6f}{an:<18.6f}{diff:.6f}")

    print("-" * 60)


def plot_probabilities(mc_probs: dict[int, float]) -> None:
    # Будує графік ймовірностей

    sums = list(range(2, 13))
    mc_values = [mc_probs[s] for s in sums]
    analytical_values = [ANALYTICAL_PROBABILITIES[s] for s in sums]

    fig = plt.figure(figsize=(10, 6))
    fig.canvas.manager.set_window_title("Монте-Карло — кидання двох кубиків")

    plt.bar(sums, mc_values, alpha=0.7, label="Monte-Carlo", color="#4A90E2")
    plt.plot(sums, analytical_values, color="red", marker="o", label="Аналітична")

    plt.xlabel("Сума двох кубиків")
    plt.ylabel("Ймовірність")
    plt.title("Ймовірності сум при киданні двох кубиків\n(Метод Монте-Карло)")
    plt.xticks(sums)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.legend()

    plt.tight_layout()
    plt.show()


def main():
    ROLLS = 1_000_000

    mc_probabilities = monte_carlo_dice_simulation(ROLLS)
    print_probability_table(mc_probabilities)
    plot_probabilities(mc_probabilities)


if __name__ == "__main__":
    main()
