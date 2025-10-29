#!/usr/bin/env python
import sys
from pathlib import Path
from colorama import init, Fore


init(autoreset=True)  # автоматично скидає стиль після кожного кольорового виводу

def print_tree(dir_path: Path, indent: str = "    "):
    # Рекурсивно виводить структуру директорії з кольорами.
    try:
        entries = sorted(dir_path.iterdir())
    except PermissionError:
        print(indent + Fore.RED + "[Permission denied]")
        return

    for entry in entries:
        if entry.is_dir():
            print(f"{indent}{Fore.CYAN}{entry.name}/")
            print_tree(entry, indent + "    ") # виклик рекурсії
        else:
            print(f"{indent}{Fore.GREEN}{entry.name}")

def main():
    if len(sys.argv) < 2:
        print(Fore.YELLOW + "Використання: python hw03.py /шлях/до/вашої/директорії")
        return

    target = Path(sys.argv[1])

    if not target.exists():
        print(Fore.RED + f"Помилка: шлях не існує -> {target}")
        return
    
    if not target.is_dir():
        print(Fore.RED + f"Помилка: шлях не є директорією -> {target}")
        return

    print(Fore.CYAN + f"{target.resolve().name}/")
    print_tree(target, indent="    ") # головна функція

if __name__ == "__main__":
    main()
