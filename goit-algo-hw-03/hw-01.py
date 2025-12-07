import argparse
import shutil
from pathlib import Path
from typing import Optional


def parse_args() -> argparse.Namespace:
    """
    Парсинг аргументів командного рядка.
    Приклад:
        python sort_files.py C:\source C:\destination
        python sort_files.py C:\source          # destination -> dist
    """
    parser = argparse.ArgumentParser(
        description="Рекурсивно копіює файли з source до destination та сортує їх за розширеннями."
    )
    parser.add_argument(
        "source",
        type=str,
        help="Шлях до вихідної директорії (source)."
    )
    parser.add_argument(
        "destination",
        type=str,
        nargs="?",
        default="dist",
        help="Шлях до директорії призначення (destination). За замовчуванням: dist."
    )
    return parser.parse_args()


def copy_and_sort_files(
    source_dir: Path,
    dest_root: Path
) -> None:
    """
    Рекурсивно обходить source_dir і копіює файли в dest_root,
    розкладаючи їх по піддиректоріях за розширеннями.
    """

    try:
        entries = list(source_dir.iterdir())
    except PermissionError as e:
        print(f"[ERROR] Немає доступу до директорії: {source_dir} ({e})")
        return
    except FileNotFoundError as e:
        print(f"[ERROR] Директорію не знайдено: {source_dir} ({e})")
        return
    except OSError as e:
        print(f"[ERROR] Помилка доступу до {source_dir}: {e}")
        return

    for entry in entries:
        if entry.is_dir():
            # Рекурсивно обходимо вкладену директорію
            copy_and_sort_files(entry, dest_root)
        elif entry.is_file():
            copy_single_file(entry, dest_root)


def copy_single_file(file_path: Path, dest_root: Path) -> None:
    """
    Копіює один файл у підпапку dest_root, названу за розширенням файлу.
    """
    # Отримуємо розширення без крапки, наприклад: ".txt" -> "txt"
    ext = file_path.suffix.lower().lstrip(".")
    if not ext:
        ext = "no_ext"

    dest_dir = dest_root / ext

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"[ERROR] Не вдалося створити директорію: {dest_dir} ({e})")
        return

    dest_file = dest_dir / file_path.name

    try:
        shutil.copy2(file_path, dest_file)
        print(f"[OK] {file_path} -> {dest_file}")
    except PermissionError as e:
        print(f"[ERROR] Немає прав для копіювання: {file_path} ({e})")
    except FileNotFoundError as e:
        print(f"[ERROR] Файл не знайдено під час копіювання: {file_path} ({e})")
    except OSError as e:
        print(f"[ERROR] Помилка копіювання {file_path} -> {dest_file}: {e}")


def main() -> None:
    args = parse_args()
    source = Path(args.source)
    destination = Path(args.destination)

    if not source.exists() or not source.is_dir():
        print(f"[FATAL] Вихідна директорія не існує або не є директорією: {source}")
        return

    try:
        destination.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"[FATAL] Не вдалося створити директорію призначення: {destination} ({e})")
        return

    print(f"Source: {source}")
    print(f"Destination: {destination}")
    print("Починаю копіювання...\n")

    copy_and_sort_files(source, destination)

    print("\nГотово. Усі файли скопійовано та відсортовано за розширеннями.")


if __name__ == "__main__":
    main()
