from datetime import datetime


def get_days_from_today(date: str) -> int:    
    try:
        # Перетворюємо вхідний рядок у дату прибираємо час
        user_date = datetime.strptime(date,"%Y-%m-%d").date()
    except ValueError: 
        # Якщо формат дати неправильний — повідомляємо користувача
        print("Please inter the data in the correct dataformat YYYY-MM-DD !")
    else:
        # Розраховуємо різницю між поточною датою без часу та датою що ввів коритувач
        data_diff = datetime.now().date() - user_date
        return(data_diff.days)

# Задаємо будь-яку дату
user_str = input('Enter any date in format YYYY-MM-DD : ')
# Отриманий результат виводимо користувачу
print("The difference to the current date is : "+ format(get_days_from_today(user_str)))
