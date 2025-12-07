# === ВИНЕСЕНІ КОНСТАНТИ ===

BRACKET_PAIRS = {
    ')': '(',
    ']': '[',
    '}': '{',
}

OPENING_BRACKETS = set(BRACKET_PAIRS.values())
CLOSING_BRACKETS = set(BRACKET_PAIRS.keys())


# === ФУНКЦІЯ ПЕРЕВІРКИ ===

def is_brackets_balanced(s: str) -> bool:
    # Перевіряє, чи дужки в рядку розставлені правильно.
    # Ігнорує всі символи, окрім дужок () [] {}.

    stack = []

    for ch in s:
        if ch in OPENING_BRACKETS:
            stack.append(ch)

        elif ch in CLOSING_BRACKETS:
            if not stack:
                return False
            if stack[-1] != BRACKET_PAIRS[ch]:
                return False
            stack.pop()

    return len(stack) == 0


# === ФУНКЦІЯ ВИВОДУ РЕЗУЛЬТАТУ ===

def print_result(s: str) -> None:
    print(f"{s}: {'Симетрично' if is_brackets_balanced(s) else 'Несиметрично'}")


# === ПРИКЛАДИ ===

print_result("( ){[ 1 ]( 1 + 3 )( ){ }}")
print_result("( 23 ( 2 - 3);")
print_result("( 11 }")
