class HashTable:
    def __init__(self, size):
        self.size = size
        self.table = [[] for _ in range(self.size)]

    def hash_function(self, key):
        return hash(key) % self.size

    def insert(self, key, value):
        key_hash = self.hash_function(key)
        key_value = [key, value]

        # Бакет завжди список — умовна перевірка тут не потрібна
        for pair in self.table[key_hash]:
            if pair[0] == key:
                pair[1] = value  # оновлення
                return True

        # Якщо ключа немає — додаємо
        self.table[key_hash].append(key_value)
        return True

    def get(self, key):
        key_hash = self.hash_function(key)
        for pair in self.table[key_hash]:
            if pair[0] == key:
                return pair[1]
        return None

    def delete(self, key):
        """Видаляє пару key-value. Повертає True або False."""
        key_hash = self.hash_function(key)
        bucket = self.table[key_hash]

        for i, pair in enumerate(bucket):
            if pair[0] == key:
                del bucket[i]     # видаляємо пару
                return True

        return False  # ключа немає

# Тестуємо хеш-таблицю:
H = HashTable(5)
H.insert("apple", 10)
H.insert("orange", 20)
H.insert("banana", 30)

print(H.get("apple"))     # 10
print(H.get("orange"))    # 20
print(H.get("banana"))    # 30

print(H.delete("orange")) # True
print(H.get("orange"))    # None

print(H.delete("grape"))  # False (немає такого ключа)
