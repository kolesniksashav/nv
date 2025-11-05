from collections import UserDict
from typing import List, Optional


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
        if not (digits.isdigit() and len(digits) == 10):
            raise ValueError("Phone must contain exactly 10 digits.")
        self.value = digits


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        #self.phones: List[Phone] = []

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
