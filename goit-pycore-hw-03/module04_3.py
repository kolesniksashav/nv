import re

def normalize_phone(phone_number: str) -> str:
    # чи phone_number є рядком
    if not isinstance(phone_number, str):
        raise TypeError("phone_number має бути рядком")

    # Витягуємо тільки цифри:
    digits = re.sub(r'\D', '', phone_number)
    if not digits:
        return ''  # немає цифр — нічого нормалізувати
   
    # Перевіряємо, що цифри починаються з 38
    if digits.startswith('38'): 
        return '+' + digits
    else:
        return '+38' + digits
    
# Приклад введення данних
raw_numbers = [
    "067\t123 4567",
    "(095) 234-5678\n",
    "+380 44 123 4567",
    "380501234567",
    "    +38(050)123-32-34",
    "     0503451234",
    "(050)8889900",
    "38050-111-22-22",
    "38050 111 22 11   ",
]

sanitized_numbers = [normalize_phone(num) for num in raw_numbers]
print("Нормалізовані номери телефонів для SMS-розсилки:", sanitized_numbers)
# Вивід:
# ['+380671234567', '+380952345678', '+380441234567', 
# '+380501234567', '+380501233234',  '+380503451234', 
# '+380508889900', '+380501112222', '+380501112211']
