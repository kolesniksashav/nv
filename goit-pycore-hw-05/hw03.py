#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Лог-аналізатор:
- Читає файл логів (аргумент #1)
- Опційно приймає рівень логування для фільтрації (аргумент #2): info|error|debug|warning
- Друкує таблицю з кількістю записів за рівнями
- Якщо вказано рівень — також друкує деталі записів цього рівня
"""

from __future__ import annotations
import argparse
from typing import List, Dict, Iterable
from collections import Counter
import sys

# Допустимі рівні — для валідації та нормалізації
LEVELS = ("INFO", "DEBUG", "ERROR", "WARNING")


def parse_log_line(line: str) -> dict:
    """
    Парсить один рядок логу у словник.
    Очікуваний формат:
        YYYY-MM-DD HH:MM:SS LEVEL Message...
    Повертає словник з ключами: date, time, level, message.
    Якщо рядок некоректний — піднімає ValueError.
    """
    # Розбиваємо на 4 частини: дата, час, рівень, та решта — повідомлення
    parts = line.strip().split(maxsplit=3)
    if len(parts) < 4:
        raise ValueError("Некоректний формат рядка логу")

    date, timestr, level, message = parts[0], parts[1], parts[2], parts[3]

    # Базова валідація рівня
    lvl = level.upper()
    if lvl not in LEVELS:
        raise ValueError(f"Непідтримуваний рівень: {level}")

    return {"date": date, "time": timestr, "level": lvl, "message": message}


def load_logs(file_path: str) -> List[dict]:
    """
    Зчитує файл логів, парсить кожен рядок через parse_log_line.
    Пропускає порожні рядки, некоректні рядки логу логічно ігнорує (з попередженням у stderr).
    """
    logs: List[dict] = []
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            for i, raw in enumerate(fh, start=1):
                line = raw.strip()
                if not line:
                    continue
                try:
                    entry = parse_log_line(line)
                    logs.append(entry)
                except ValueError as e:
                    print(f"[WARN] Рядок {i} пропущено: {e}", file=sys.stderr)
    except FileNotFoundError:
        print(f"[ERR] Файл не знайдено: {file_path}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"[ERR] Помилка читання файлу: {e}", file=sys.stderr)
        sys.exit(1)

    return logs


def filter_logs_by_level(logs: List[dict], level: str) -> List[dict]:
    """
    Повертає лише записи з потрібним рівнем (регістр неважливий).
    Використано елемент FP: filter + лямбда.
    """
    normalized = level.upper()
    if normalized not in LEVELS:
        raise ValueError(f"Невідомий рівень: {level}")
    return list(filter(lambda rec: rec["level"] == normalized, logs))


def count_logs_by_level(logs: Iterable[dict]) -> Dict[str, int]:
    """
    Підрахунок кількості за рівнями. FP-елементи: генераторний вираз.
    Гарантуємо наявність усіх рівнів у вихідному словнику (навіть якщо 0).
    """
    c = Counter(rec["level"] for rec in logs)
    return {lvl: c.get(lvl, 0) for lvl in LEVELS}


def display_log_counts(counts: Dict[str, int]) -> None:
    """
    Друкує таблицю з підрахунком записів для кожного рівня.
    """
    left = "Рівень логування"
    right = "Кількість"
    sep = "-" * 17 + "|" + "-" * 10
    # Вирівнювання колонок
    print(f"{left:<17} | {right:<8}")
    print(sep)
    for lvl in LEVELS:
        print(f"{lvl:<17} | {counts.get(lvl, 0):<8}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Аналізатор логів: статистика та фільтрація за рівнем."
    )
    parser.add_argument(
        "file_path",
        help="Шлях до файлу логів"
    )
    parser.add_argument(
        "level",
        nargs="?",
        help="Опційно: рівень логування для детального виводу (info|error|debug|warning)"
    )
    args = parser.parse_args()

    logs = load_logs(args.file_path)

    # Якщо файл порожній або всі рядки зіпсовані
    if not logs:
        print("[INFO] Не знайдено жодного коректного запису у файлі.", file=sys.stderr)
        display_log_counts({lvl: 0 for lvl in LEVELS})
        return

    counts = count_logs_by_level(logs)
    display_log_counts(counts)

    # Якщо передано рівень — покажемо деталі для нього
    if args.level:
        try:
            selected = filter_logs_by_level(logs, args.level)
        except ValueError as e:
            print(f"[ERR] {e}", file=sys.stderr)
            sys.exit(2)

        norm_level = args.level.upper()
        print(f"\nДеталі логів для рівня '{norm_level}':")
        if not selected:
            print("(Немає записів.)")
            return

        # FP-елемент: map для форматування вихідних рядків
        lines = map(
            lambda r: f"{r['date']} {r['time']} - {r['message']}",
            selected
        )
        for out in lines:
            print(out)


if __name__ == "__main__":
    main()
