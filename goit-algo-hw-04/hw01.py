import random
import timeit
from typing import List, Callable, Dict


# ---------- Алгоритми сортування ----------

def insertion_sort(data: List[int]) -> List[int]:
    # Сортування вставками (in-place). Повертає відсортований список.
    arr = data[:]  # не псуємо вихідний список
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def merge_sort(data: List[int]) -> List[int]:
    # Сортування злиттям. Повертає новий відсортований список.
    if len(data) <= 1:
        return data[:]

    mid = len(data) // 2
    left = merge_sort(data[:mid])
    right = merge_sort(data[mid:])

    return merge(left, right)


def merge(left: List[int], right: List[int]) -> List[int]:
    # Зливає два відсортовані списки.
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def timsort(data: List[int]) -> List[int]:
    # Використовує вбудований Timsort (sorted).
    return sorted(data)


# ---------- Генерація даних ----------

def generate_data(n: int) -> Dict[str, List[int]]:
    # Генерує випадковий, відсортований та реверсований масиви.
    random_list = [random.randint(0, 1_000_000) for _ in range(n)]
    sorted_list = sorted(random_list)
    reversed_list = sorted_list[::-1]

    return {
        "random": random_list,
        "sorted": sorted_list,
        "reversed": reversed_list,
    }


# ---------- Вимірювання часу ----------

def benchmark_sort(
    func: Callable[[List[int]], List[int]],
    data: List[int],
    repeats: int = 3
) -> float:
    
    # Вимірює середній час виконання func на копії data.
    # Використовує timeit.timeit.

    def wrapper():
        func(data[:])  # кожен раз сортуємо копію

    t = timeit.timeit(wrapper, number=repeats)
    return t / repeats


def run_benchmarks():
    sizes = [1_000, 5_000, 10_000]
    algorithms: Dict[str, Callable[[List[int]], List[int]]] = {
        "insertion_sort": insertion_sort,
        "merge_sort": merge_sort,
        "timsort(sorted)": timsort,
    }

    repeats = 3

    print("Результати в секундах (середнє за", repeats, "запуски):")
    print()
    print(f"{'size':>6} | {'type':>9} | {'algorithm':>15} | {'time':>10}")
    print("-" * 50)

    for n in sizes:
        datasets = generate_data(n)

        for data_type, data in datasets.items():
            for name, func in algorithms.items():
                t = benchmark_sort(func, data, repeats=repeats)
                print(f"{n:6} | {data_type:9} | {name:15} | {t:10.6f}")


if __name__ == "__main__":
    run_benchmarks()
