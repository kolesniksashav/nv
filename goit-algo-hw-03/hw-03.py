def hanoi(n: int, source: str, target: str, auxiliary: str, pegs: dict) -> None:
    """
    Рекурсивно переміщує n дисків зі стрижня source на стрижень target,
    використовуючи auxiliary як допоміжний. Стан тримаємо в словнику pegs.
    """
    if n == 0:
        return

    # 1. Перемістити n-1 дисків із source на auxiliary
    hanoi(n - 1, source, auxiliary, target, pegs)

    # 2. Перемістити найбільший диск із source на target
    disk = pegs[source].pop()   # знімаємо верхній диск (останній у списку)
    pegs[target].append(disk)
    print(f"Перемістити диск з {source} на {target}: {disk}")
    print(f"Проміжний стан: {pegs}")

    # 3. Перемістити n-1 дисків із auxiliary на target
    hanoi(n - 1, auxiliary, target, source, pegs)


def main():
    # Ввід кількості дисків
    while True:
        user_input = input("Введіть кількість дисків n (n ≥ 1): ")
        try:
            n = int(user_input)
            if n < 1:
                print("n має бути цілим числом ≥ 1. Спробуйте ще раз.")
                continue
            break
        except ValueError:
            print("Потрібно ввести ціле число. Спробуйте ще раз.")

    # Початковий стан: на стрижні A — диски [n, ..., 1]
    pegs = {
        'A': list(range(n, 0, -1)),  # [n, n-1, ..., 1]
        'B': [],
        'C': []
    }

    print(f"Початковий стан: {pegs}")

    # Запускаємо рекурсію: з A на C, використовуючи B
    hanoi(n, 'A', 'C', 'B', pegs)

    print(f"Кінцевий стан: {pegs}")


if __name__ == "__main__":
    main()
