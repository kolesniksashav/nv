import timeit
from pathlib import Path
from collections import defaultdict

# =========================
# 1. Читання текстових файлів
# =========================

TEXT1_PATH = "стаття 1.txt"
TEXT2_PATH = "стаття 2.txt"

text1 = Path(TEXT1_PATH).read_text(encoding="utf-8", errors="ignore")
text2 = Path(TEXT2_PATH).read_text(encoding="utf-8", errors="ignore")


# =========================
# 2. Алгоритми пошуку підрядка
# =========================

def boyer_moore(text: str, pattern: str) -> int:
    m, n = len(pattern), len(text)
    if m == 0:
        return 0

    # Таблиця "поганого символу"
    bad = {}
    for i, c in enumerate(pattern):
        bad[c] = i

    s = 0
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            return s
        c = text[s + j]
        bc = bad.get(c, -1)
        s += max(1, j - bc)
    return -1


def _kmp_lps(pattern: str):
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_search(text: str, pattern: str) -> int:
    n, m = len(text), len(pattern)
    if m == 0:
        return 0

    lps = _kmp_lps(pattern)
    i = j = 0

    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                return i - j
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return -1


def rabin_karp(text: str, pattern: str, d: int = 256, q: int = 101) -> int:
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    if m > n:
        return -1

    h = pow(d, m - 1, q)
    p = 0  # хеш патерна
    t = 0  # хеш першого вікна в тексті

    for i in range(m):
        p = (d * p + ord(pattern[i])) % q
        t = (d * t + ord(text[i])) % q

    for s in range(n - m + 1):
        if p == t:
            if text[s:s + m] == pattern:
                return s
        if s < n - m:
            t = (d * (t - ord(text[s]) * h) + ord(text[s + m])) % q
            if t < 0:
                t += q
    return -1


# =========================
# 3. Вибір підрядків
# =========================

existing1 = "public static int linearSearch"
fake1 = "ZZZ_unreal_substring_1"

existing2 = "бази даних рекомендаційної си"
fake2 = "ZZZ_unreal_substring_2"

# Перевірка коректності вибору
assert existing1 in text1, "Реальний підрядок 1 не знайдено в тексті 1"
assert existing2 in text2, "Реальний підрядок 2 не знайдено в тексті 2"
assert fake1 not in text1, "Вигаданий підрядок 1 раптом знайшовся в тексті 1"
assert fake2 not in text2, "Вигаданий підрядок 2 раптом знайшовся в тексті 2"

print("Підрядки, що шукаємо:")
print("Текст 1, реальний :", repr(existing1))
print("Текст 1, вигаданий:", repr(fake1))
print("Текст 2, реальний :", repr(existing2))
print("Текст 2, вигаданий:", repr(fake2))
print()


# =========================
# 4. Вимірювання часу виконання
# =========================

def measure(func, text, pattern, number=2000):
    stmt = lambda: func(text, pattern)
    total = timeit.timeit(stmt, number=number)
    return total / number  # середній час одного виклику


algorithms = {
    "Boyer-Moore": boyer_moore,
    "KMP": kmp_search,
    "Rabin-Karp": rabin_karp,
}

# (text_id, algo_name, case) -> середній час (секунди)
results = {}

for name, f in algorithms.items():
    results[(1, name, "existing")] = measure(f, text1, existing1)
    results[(1, name, "fake")] = measure(f, text1, fake1)
    results[(2, name, "existing")] = measure(f, text2, existing2)
    results[(2, name, "fake")] = measure(f, text2, fake2)

# =========================
# 5. Обчислення середніх значень
# =========================

avg_per_text = defaultdict(float)      # (text_id, algo_name) -> сек
avg_overall = defaultdict(float)       # algo_name -> сек

for (text_id, algo_name, case), t in results.items():
    avg_per_text[(text_id, algo_name)] += t / 2.0  # 2 кейси: existing + fake

for (text_id, algo_name, case), t in results.items():
    avg_overall[algo_name] += t / 4.0  # 2 тексти × 2 кейси = 4


# =========================
# 6. Допоміжні функції для виводу в markdown
# =========================

def to_us(t: float) -> float:
    """Перевести секунди в мікросекунди."""
    return t * 1e6


def print_markdown_table(headers, rows):
    """
    Друк вирівняної markdown-таблиці.
    headers: список заголовків
    rows: список рядків (кожен — список значень)
    """
    # Ширина колонок
    col_widths = []
    for i in range(len(headers)):
        max_len = len(str(headers[i]))
        for row in rows:
            max_len = max(max_len, len(str(row[i])))
        col_widths.append(max_len)

    # Заголовок
    header_row = "| " + " | ".join(
        str(headers[i]).ljust(col_widths[i]) for i in range(len(headers))
    ) + " |"

    # Роздільник
    separator_row = "|-" + "-|-".join(
        "-" * col_widths[i] for i in range(len(headers))
    ) + "-|"

    print(header_row)
    print(separator_row)

    # Рядки з даними
    for row in rows:
        print(
            "| "
            + " | ".join(
                str(row[i]).ljust(col_widths[i]) for i in range(len(headers))
            )
            + " |"
        )


# =========================
# 7. Вивід результатів у форматі Markdown
# =========================

# Таблиця 1 — час пошуку для кожного випадку
headers1 = ["Випадок", "Boyer–Moore (мкс)", "KMP (мкс)", "Rabin–Karp (мкс)"]
rows1 = []

for text_id in [1, 2]:
    for case, case_uk in [
        ("existing", "наявний підрядок"),
        ("fake", "вигаданий підрядок"),
    ]:
        rows1.append([
            f"Текст {text_id}, {case_uk}",
            f"{to_us(results[(text_id, 'Boyer-Moore', case)]):.1f}",
            f"{to_us(results[(text_id, 'KMP', case)]):.1f}",
            f"{to_us(results[(text_id, 'Rabin-Karp', case)]):.1f}",
        ])

print("\n### Таблиця 1. Час пошуку (мкс)\n")
print_markdown_table(headers1, rows1)


# Таблиця 2 — середній час по кожному тексту
headers2 = ["Текст", "Алгоритм", "Середній час, мкс"]
rows2 = []

for text_id in [1, 2]:
    for name in ["Boyer-Moore", "KMP", "Rabin-Karp"]:
        rows2.append([
            str(text_id),
            name,
            f"{to_us(avg_per_text[(text_id, name)]):.1f}",
        ])

print("\n### Таблиця 2. Середній час по текстах\n")
print_markdown_table(headers2, rows2)


# Таблиця 3 — середній час по всіх експериментах
headers3 = ["Алгоритм", "Середній час по всіх тестах, мкс"]
rows3 = []

for name in ["Boyer-Moore", "KMP", "Rabin-Karp"]:
    rows3.append([
        name,
        f"{to_us(avg_overall[name]):.1f}",
    ])

print("\n### Таблиця 3. Середній час по всіх експериментах\n")
print_markdown_table(headers3, rows3)
