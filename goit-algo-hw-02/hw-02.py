from collections import deque

def is_palindrome(text: str) -> bool:
    # очищаємо від пробілів і знижуємо регістр
    cleaned = "".join(ch.lower() for ch in text if ch != " ")
    
    # додаємо символи в deque
    d = deque(cleaned)

    # порівняння символів з обох кінців
    while len(d) > 1:
        if d.popleft() != d.pop():
            return False

    return True


# Приклади використання
print(is_palindrome("Racecar"))          # True
print(is_palindrome("A man a plan a canal Panama"))  # True
print(is_palindrome("Hello"))            # False
