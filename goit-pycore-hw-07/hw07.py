
from collections import UserDict
from typing import List, Optional, Callable, Dict, Tuple
from datetime import datetime, date, timedelta
import calendar


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if value == '':
            raise ValueError("Name must be a non-empty string.")
        self.value = value.strip()

class Phone(Field):
    def __init__(self, value):
        digits = value.strip()
        if not digits.isdigit() or len(digits) != 10:
            raise ValueError("Phone must contain exactly 10 digits.")
        self.value = digits


class Birthday(Field):
    #Зберігає дату народження як datetime.date (формат вводу DD.MM.YYYY).
    @property
    def value(self) -> date:
        return self._value

    @value.setter
    def value(self, v: str | date) -> None:
        if isinstance(v, date):
            self._value = v
            return
        try:
            dt = datetime.strptime(v.strip(), "%d.%m.%Y").date()
        except Exception:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        self._value = dt


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str) -> Phone:
        p = Phone(phone)
        self.phones.append(p)
        return p

    def remove_phone(self, phone: str) -> bool:
        # Видаляє перший збіг; повертає True/False за фактом видалення.
        for i, p in enumerate(self.phones):
            if p.value == phone:
                del self.phones[i]
                return True
        return False

    def edit_phone(self, old_phone: str, new_phone: str) -> bool:
        # Замінює перший збіг old_phone на new_phone; True якщо успішно.
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone  # пройде валідацію Phone
                return True
        return False

    def find_phone(self, phone: str) -> Optional[Phone]:
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday_str: str) -> None:
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

        
class AddressBook(UserDict):
    def add_record(self, record: Record):
        key = record.name.value
        if key in self.data:
            raise ValueError(f"Record with name '{key}' already exists.")
        self.data[key] = record

    def find(self, name: str):
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self, today: Optional[date] = None) -> Dict[str, List[str]]:
        #Повертає словник {weekday_name: [names, ...]} для ДН у найближчі 7 днів.
        #Якщо ДН припадає на вихідні (сб/нд), переносимо вітання на понеділок.

        if today is None:
            today = date.today()

        # межа вікна 7 днів (без урахування минулих)
        window_end = today + timedelta(days=7)
        result: Dict[str, List[str]] = {}

        for rec in self.data.values():
            if not rec.birthday:
                continue
            bday = rec.birthday.value

            # наступний ДН у поточному або наступному році
            candidate = bday.replace(year=today.year)
            if candidate < today:
                candidate = bday.replace(year=today.year + 1)

            # у вікні 7 днів?
            if today <= candidate <= window_end:
                wd = candidate.weekday()  # 0=Mon ... 6=Sun
                # якщо субота/неділя — переносимо на понеділок
                if wd in (5, 6):
                    # знайти понеділок
                    days_to_monday = (7 - wd) % 7
                    candidate = candidate + timedelta(days=days_to_monday)
                weekday_name = calendar.day_name[candidate.weekday()]
                result.setdefault(weekday_name, []).append(rec.name.value)

        # сортуємо імена для стабільного виводу
        for k in result:
            result[k].sort(key=str.casefold)
        return result
    

def parse_input(user_input: str) -> Tuple[str, List[str]]:
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


# ==========================
# ДЕКОРАТОР ПОМИЛОК
# ==========================
def input_error(func: Callable) -> Callable:
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except IndexError:
            fname = func.__name__
            if fname == "add_contact":
                return "Give me name and phone please."
            if fname == "change_contact":
                return "Give me name, old phone and new phone please."
            if fname in {"show_phone", "show_birthday", "add_birthday"}:
                return "Enter user name."
            return "Not enough arguments."
        except ValueError as e:
            return str(e) if str(e) else "Wrong input. Try again."
    return inner
    
@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    name, phone, *_ = args  # IndexError -> decorator
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)  # ValueError всередині Phone -> decorator
    return message


@input_error
def change_contact(args: List[str], book: AddressBook) -> str:
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    if not record.edit_phone(old_phone, new_phone):
        return "Old phone not found."
    return "Contact updated."


@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    phones = ", ".join(p.value for p in record.phones) if record.phones else "(no phones)"
    return f"{name}: {phones}"


@input_error
def show_all(_: List[str], book: AddressBook) -> str:
    if not book.data:
        return "(No contacts yet)"
    lines = [str(rec) for rec in book.data.values()]
    return "\n".join(lines)


@input_error
def add_birthday(args: List[str], book: AddressBook) -> str:
    name, bday_str, *_ = args
    record = book.find(name)
    if record is None:
        # Автоматично створюємо контакт, якщо його не було
        record = Record(name)
        book.add_record(record)
        created = True
    else:
        created = False
    record.add_birthday(bday_str)  # ValueError при неправильному форматі
    return "Birthday added." if created else "Birthday updated."


@input_error
def show_birthday(args: List[str], book: AddressBook) -> str:
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    if not record.birthday:
        return f"{name} has no birthday set."
    return record.birthday.value.strftime("%d.%m.%Y")


@input_error
def birthdays(_: List[str], book: AddressBook) -> str:
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    # Гарний формат: день тижня: імена, через кому
    order = list(calendar.day_name)  # Monday..Sunday
    parts = []
    for day in order:
        if day in upcoming:
            parts.append(f"{day}: {', '.join(upcoming[day])}")
    return "\n".join(parts)


# ==========================
# ГОЛОВНИЙ ЦИКЛ
# ==========================
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()