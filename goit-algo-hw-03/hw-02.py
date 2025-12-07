import turtle

def koch_curve(t, order, size):
    """
    Рекурсивно малює одну криву Коха.
    t      – обʼєкт turtle.Turtle
    order  – рівень рекурсії (0, 1, 2, 3, ...)
    size   – довжина відрізка
    """
    if order == 0:
        t.forward(size)
    else:
        # Чотири відрізки з поворотами між ними:
        # F -> F-F++F-F у термінах L-системи
        for angle in [60, -120, 60, 0]:
            koch_curve(t, order - 1, size / 3)
            t.left(angle)


def draw_koch_snowflake(order, size=300):
    # Малює повну сніжинку Коха (3 криві Коха по колу).

    window = turtle.Screen()
    window.bgcolor("white")
    window.title(f"Koch Snowflake (order={order})")

    t = turtle.Turtle()
    t.speed(0)  # максимальна швидкість
    t.penup()
    # Трохи зміщуємо сніжинку, щоб вона була по центру
    t.goto(-size / 2, size / 3)
    t.pendown()

    # Малюємо три сторони трикутника
    for _ in range(3):
        koch_curve(t, order, size)
        t.right(120)

    # Не закриваємо вікно автоматично
    window.mainloop()


def main():
    while True:
        user_input = input("Введіть рівень рекурсії (ціле число >= 0): ")
        try:
            order = int(user_input)
            if order < 0:
                print("Рівень рекурсії має бути невідʼємним. Спробуйте ще раз.")
                continue
            break
        except ValueError:
            print("Потрібно ввести ціле число. Спробуйте ще раз.")

    draw_koch_snowflake(order)


if __name__ == "__main__":
    main()
