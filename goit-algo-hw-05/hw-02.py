def binary_search_upper_bound(arr, target):
    """
    arr - відсортований список (у т.ч. з дробовими числами)
    target - значення для пошуку

    Повертає (iterations, upper_bound)
    """
    left = 0
    right = len(arr) - 1
    iterations = 0
    upper_bound = None

    while left <= right:
        iterations += 1
        mid = (left + right) // 2

        if arr[mid] == target:
            return iterations, arr[mid]  # ← негайний вихід

        if arr[mid] > target:
            upper_bound = arr[mid]
            right = mid - 1
        else:
            left = mid + 1

    return iterations, upper_bound

# Тестуємо B-пошук:
arr = [0.5, 1.2, 2.8, 3.3, 4.0, 5.1, 8.7]

print(binary_search_upper_bound(arr, 3.0))
print(binary_search_upper_bound(arr, 3.3))
print(binary_search_upper_bound(arr, 10))
print(binary_search_upper_bound(arr, 0.5))
print(binary_search_upper_bound(arr, 2.8))
