import re
from decimal import Decimal
from typing import Callable, Generator


# Патерн: число зі знаком/без, ціла або з десятковою крапкою.
# Обмеження (?<!\S) / (?!\S) гарантують, що число відокремлене пробілами або межами рядка.
NUMBER_PATTERN = re.compile(r'(?<!\S)[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?!\S)')


def generator_numbers(text: str) -> Generator[Decimal, None, None]:
    """
    Генерує усі дійсні числа з тексту як Decimal.
    Вимога задачі: числа відокремлені пробілами з обох боків.
    """
    for m in NUMBER_PATTERN.finditer(text):
        # Decimal гарантує точність для грошових сум
        yield Decimal(m.group())

def sum_profit(text: str, func: Callable[[str], Generator[Decimal, None, None]]) -> Decimal:
    """
    Повертає суму всіх чисел, знайдених генератором `func`.
    Повертаємо Decimal, щоб уникнути похибок з плаваючою крапкою.
    """
    total = Decimal(0)
    for value in func(text):
        total += value
    return total

text = (
    "Загальний дохід працівника складається з декількох частин: "
    "1000.01 як основний дохід, доповнений додатковими надходженнями "
    "27.45 і 324.00 доларів."
)

total_income = sum_profit(text, generator_numbers)
print(f"Загальний дохід: {total_income}")  # Очікувано: 1351.46
