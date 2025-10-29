import pathlib


def get_cats_info(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as file:            
            cats_list = []

            for line in file:
                # Прибираємо зайві пробіли та символи нового рядка
                line = line.strip()
                if not line:  # пропускаємо порожні рядки
                    continue

                id, name, age = line.split(',')
                cat_dict = {
                    "id": id,
                    "name": name,
                    "age": age
                }
                cats_list.append(cat_dict)

            return cats_list

    except FileNotFoundError:
        print(f"Помилка: файл '{path}' не знайдено.")
    except ValueError:
        print("Помилка: рядок має неправильний формат (повинно бути 3 елементи, розділені комами).")

def main():
    filename = "cats_file_.txt"
    full_name = pathlib.Path(__file__).parent / filename

    cats_info = get_cats_info(full_name)

    print(cats_info)

if __name__ == "__main__":
    main()