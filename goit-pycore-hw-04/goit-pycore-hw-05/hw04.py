from typing import Callable


# ====== Декоратор обробки помилок ======
def input_error(func: Callable) -> Callable:
    """
    Перехоплює базові помилки введення та повертає дружні повідомлення,
    не зупиняючи роботу програми.
    """
    def inner(*args, **kwargs):
        fname = func.__name__ # ім'я функції
        try:
            # попередні перевірки
            if fname == "show_all":
                contacts = args # аргументи функції
            else:
                cmd_args, contacts = args # аргументи функції
            
            match fname:
                case "add_contact":
                    if cmd_args[0] in contacts:
                        raise KeyError
                    if len(cmd_args) < 2:
                        raise IndexError  # бракує аргументів                           
                    phone = validate_phone(cmd_args[1])
                case "change_contact":
                    if len(cmd_args) < 2:
                        raise IndexError  # бракує аргументів                        
                    if not cmd_args[0] in contacts:
                        raise KeyError
                    phone = validate_phone(cmd_args[1])
                case "show_phone": 
                    if not cmd_args[0] in contacts:
                        raise KeyError
            # Виклик функції
            return func(*args, **kwargs)
        except KeyError:            
            if fname == "add_contact":
                return "Contact already exists."
            return "Contact not found."
        except IndexError:
            # Немає потрібних аргументів
            if fname == "add_contact":
                return "Give me name and phone please."
            elif fname == "change_contact":
                return "Give me name and new phone please."
            elif fname == "show_phone":
                return "Enter user name."
            return "Not enough arguments."
        except ValueError as e:
            # Некоректний формат аргументів (повідомлення з функції або загальне)
            return str(e) if str(e) else "Wrong input. Try again."
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def validate_phone(phone: str) -> str:
    """
    Проста валідація телефону: лише цифри, довжина 7–15.
    Можна замінити своїм правилом.
    """
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 7 or len(digits) > 15:
        raise ValueError("Phone must contain 7–15 digits.")
    return digits

@input_error
def add_contact(args, contacts):
    name, phone = args
    contacts[name] = phone
    return "Contact added."

@input_error
def change_contact(args, contacts):
    name, phone = args
    contacts[name] = phone
    return "Contact updated."

@input_error
def show_phone(args, contacts):
    return format(contacts.get(args[0]))

@input_error
def show_all(contacts):
    return format(contacts)

def main():
    contacts = {}
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))            
        elif command == "all":
            print(show_all(contacts))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
