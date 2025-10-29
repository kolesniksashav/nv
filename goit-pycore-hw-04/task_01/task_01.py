import pathlib


def total_salary(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            counter = 0
            sums = 0

            for line in file:
                # Прибираємо пробіли та символи нового рядка
                line = line.strip()
                if not line:  # пропускаємо порожні рядки
                    continue

                _, salary_str = line.split(',')
                salary = float(salary_str)
                counter += 1
                sums += salary

            # Якщо файл порожній — повертаємо нулі
            if counter == 0:
                return (0, 0)

            return sums, sums/counter

    except FileNotFoundError:
        print(f"Помилка: файл '{path}' не знайдено.")
    except ValueError:
        print("Помилка: некоректні дані у файлі (не можна перетворити зарплату у число).")

def main():
    filename = "salary_file.txt"
    full_name = pathlib.Path(__file__).parent / filename

    total, average = total_salary(full_name)

    print(f"Загальна сума заробітної плати: {total}, Середня заробітна плата: {average}")

if __name__ == "__main__":
    main()