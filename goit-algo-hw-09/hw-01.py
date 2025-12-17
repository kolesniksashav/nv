import timeit

# Набір монет (канонічна система)
COINS = [50, 25, 10, 5, 2, 1]


def find_coins_greedy(amount, coins=COINS):
    """
    Жадібний алгоритм видачі решти.
    Спочатку використовує найбільші номінали.
    Повертає словник {номінал: кількість}.
    """
    result = {}
    remaining = amount

    for coin in coins:
        if remaining <= 0:
            break

        count = remaining // coin
        if count > 0:
            result[coin] = count
            remaining -= coin * count

    return result


def find_min_coins(amount, coins=COINS):
    """
    Алгоритм динамічного програмування.
    Гарантує мінімальну кількість монет.
    Повертає словник {номінал: кількість}.
    """
    # dp[x] — мінімальна кількість монет для суми x
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0

    # prev[x] — монета, використана останньою для суми x
    prev = [-1] * (amount + 1)

    for x in range(1, amount + 1):
        for coin in coins:
            if coin <= x and dp[x - coin] + 1 < dp[x]:
                dp[x] = dp[x - coin] + 1
                prev[x] = coin

    # Відновлення розв’язку
    result = {}
    current = amount
    while current > 0:
        coin = prev[current]
        if coin == -1:
            return {}  # на випадок неможливості розміну
        result[coin] = result.get(coin, 0) + 1
        current -= coin

    return dict(sorted(result.items()))


def benchmark():
    """
    Порівняння часу виконання greedy та DP для різних сум.
    """
    test_amounts = [113, 1004, 10_025, 100_007]
    repeats = 5

    print(f"{'Сума':>10} | {'Greedy (s)':>12} | {'DP (s)':>12}")
    print("-" * 40)

    for amount in test_amounts:
        t_greedy = timeit.timeit(
            lambda: find_coins_greedy(amount),
            number=repeats
        ) / repeats

        t_dp = timeit.timeit(
            lambda: find_min_coins(amount),
            number=repeats
        ) / repeats

        print(f"{amount:10} | {t_greedy:12.6f} | {t_dp:12.6f}")


def main():
    amount = 113

    print("Сума:", amount)
    print("Greedy:", find_coins_greedy(amount))
    print("DP:", find_min_coins(amount))
    print("\nПорівняння швидкодії:")
    benchmark()


if __name__ == "__main__":
    main()
