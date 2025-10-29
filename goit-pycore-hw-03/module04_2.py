import random


def get_numbers_ticket(min:int, max: int, quantity: int) -> list:
    # перевірка вимог до параметрів
    if not (1 <= min <= max <= 1000 and 1 <= quantity <= (max - min + 1)):
        print("Error: values must be between 1 and 1000 and the quantity must not exceed the range")
        return []

    # створити діапазон від min до max, відібрати quantity елементів та відсортувати
    return sorted(random.sample(range(min, max + 1), quantity))

min = int(input("Enter min : "))
max = int(input("Enter max : "))
quantity = int(input("Enter quantity : "))

# вивести отриманий лист елементів
print("Your lottery numbers:", get_numbers_ticket(min,max,quantity))