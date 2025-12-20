import random
from scipy.integrate import quad


def f(x):
    # Функція, f(x) = x^2
    return x ** 2

def monte_carlo_integral(func, a, b, n=1_000_000):
    """
    Обчислення визначеного інтеграла методом Монте-Карло
    (метод середнього значення).

    func — функція, яку інтегруємо
    a, b — межі інтегрування
    n — кількість випадкових точок (чим більше, тим точніше результат)
    """

    # Змінна для накопичення суми значень функції
    # у випадково згенерованих точках
    total = 0.0

    # Основний цикл методу Монте-Карло
    # На кожній ітерації:
    # 1) випадково вибираємо точку x з інтервалу [a, b]
    # 2) обчислюємо значення функції в цій точці
    # 3) додаємо це значення до загальної суми
    for _ in range(n):
        # Випадкове число з рівномірного розподілу на [a, b]
        x = random.uniform(a, b)
        # Накопичуємо суму значень функції в точці x
        total += func(x)

    # Середнє значення функції на інтервалі [a, b]
    average_value = total / n

    # Згідно з теорією:
    # ∫[a,b] f(x) dx ≈ (b - a) * (середнє значення f(x))
    integral_estimate = (b - a) * average_value

    # Повертаємо наближене значення інтеграла
    return integral_estimate

def monte_carlo_dart_throwing(func, a, b, n=1_000_000):
    """
    Обчислення визначеного інтеграла методом Монте-Карло
    (метод 'dart throwing' — кидання дротиків).

    func — функція, яку інтегруємо
    a, b — межі інтегрування по осі x
    n — кількість випадкових точок (чим більше, тим точніше)
    """

    # Максимальне значення функції на відрізку [a, b].
    # Для f(x) = x^2 на [0, 2] максимум досягається в точці x = 2
    f_max = func(b)

    # Лічильник точок, які потрапили під графік функції
    hits = 0

    # Генеруємо n випадкових точок у прямокутнику
    # x ∈ [a, b], y ∈ [0, f_max]
    for _ in range(n):
        # Випадкова координата x на відрізку інтегрування
        x = random.uniform(a, b)

        # Випадкова координата y від 0 до максимального значення функції
        y = random.uniform(0, f_max)

        # Перевіряємо, чи знаходиться точка під графіком функції
        # Якщо y <= f(x), точка належить площі інтеграла
        if y <= func(x):
            hits += 1

    # Площа прямокутника, в якому "кидаємо дротики"
    rectangle_area = (b - a) * f_max

    # Частка точок під графіком приблизно дорівнює
    # відношенню площі під кривою до площі прямокутника
    # Тому інтеграл ≈ rectangle_area * (hits / n)
    integral_estimate = rectangle_area * hits / n

    return integral_estimate

def main():
    a, b = 0, 2
    samples = 1_000_000

    mc_i_result = monte_carlo_integral(f, a, b, samples)
    mc_dd_result = monte_carlo_dart_throwing(f, a, b, samples)
    analytic_result = 8 / 3
    quad_result, _ = quad(f, a, b)

    print(f"Метод серенього Монте-Карло: {mc_i_result}, похибка:", abs(mc_i_result - analytic_result))
    print(F"Метод з дротиками Монте-Карло: {mc_dd_result}, похибка:", abs(mc_dd_result - analytic_result))
    print("Аналітичний результат:", analytic_result)
    print("quad (SciPy):", quad_result)

if __name__ == "__main__":
    main()
