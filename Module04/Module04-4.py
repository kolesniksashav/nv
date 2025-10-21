from datetime import datetime, date, timedelta

def parse_birthday(bday_str: str) -> date:
    # Парсить 'YYYY.MM.DD' у date. Повертає None при помилці формату.
    try:
        return datetime.strptime(bday_str.strip(), "%Y.%m.%d").date()
    except ValueError:
        return None

def shift_to_monday_if_weekend(d: date) -> date:
    # Якщо дата у вихідні, переносить на наступний понеділок.
    if d.weekday() == 5:  # субота
        return d + timedelta(days=2)
    if d.weekday() == 6:  # неділя
        return d + timedelta(days=1)
    return d

def birthday_this_or_next_year(bday: date, today: date) -> date:
    # Повертає дату дня народження у невисокосний рік якщо якщо народився 29 лютого.
    year = today.year
    try:
        candidate = bday.replace(year=year)
    except ValueError:
        # Якщо 29 лютого, а рік невисокосний → переносимо на 28 лютого
        candidate = date(year, 2, 28)
      
    if candidate < today:
        year += 1
        candidate = candidate.replace(year=year)
    
    return candidate

def get_upcoming_birthdays(users: list[dict], today: date) -> list[dict]:
    """
    Повертає список словників виду:
      {"congratulation_date": "YYYY.MM.DD","name": <ім'я>}
    для всіх користувачів, у кого ДН у найближчі 7 днів (включно з сьогодні).
    Якщо ДН на вихідні (сб/нд) — дата привітання переноситься на понеділок.
    """

    result = []

    for user in users:
        name = user.get("name")
        b_day = user.get("birthday")

        if isinstance(name, str) and isinstance(b_day, str):
            bday = parse_birthday(b_day)
            if bday:
                next_bday = birthday_this_or_next_year(bday, today)
                congrats_date = shift_to_monday_if_weekend(next_bday)
                horizon = today + timedelta(days=7)
                if today <= congrats_date <= horizon:
                    result.append({
                        "congratulation_date": congrats_date.strftime("%Y.%m.%d"),
                        "name": name
                    })

    return result


# Приклади
employees = [
    {"name": "John Doe", "birthday": "1985.12.31"},  # 2005,2006,2016,2017 роки де 31 грудня вихідний
    {"name": "Mike Doe", "birthday": "1980.01.02"},
    {"name": "Jane Smith", "birthday": "1990.01.27"},  # 27 січня (звичайний кейс)
    {"name": "Sam Smith", "birthday": "1980.01.25"},
    {"name": "Leap Guy", "birthday": "2000.02.29"}  # 2000 високосний
]

test_days = [date(2005, 1, 25), date(2005, 12, 30), date(2004, 2, 27)]


for tday in test_days:
    upcoming = get_upcoming_birthdays(employees, tday)
    print(f"Сьогодні: {tday}")
    print("Список привітань на цьому тижні:")
    for u in upcoming:
        print(u)
