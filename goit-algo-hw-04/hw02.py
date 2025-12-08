def merge(left, right):
    merged = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    # Додаємо залишки
    while left_index < len(left):
        merged.append(left[left_index])
        left_index += 1

    while right_index < len(right):
        merged.append(right[right_index])
        right_index += 1

    return merged

def merge_k_lists(lists):
    """
    Оптимізоване злиття k відсортованих списків.
    Ідея: зливаємо списки ПОПАРНО, як у турнірній сітці.
    Складність: O(N log k), де N — загальна кількість елементів.
    """
    if not lists:
        return []
    if len(lists) == 1:
        return lists[0]

    current_lists = lists

    # поки не залишиться один список
    while len(current_lists) > 1:
        new_lists = []

        # беремо списки по два
        for i in range(0, len(current_lists), 2):
            if i + 1 < len(current_lists):
                merged = merge(current_lists[i], current_lists[i + 1])
                new_lists.append(merged)
            else:
                # непарний "хвіст" просто переносимо
                new_lists.append(current_lists[i])

        current_lists = new_lists

    # залишився один відсортований список
    return current_lists[0]

# --- ТЕСТ ---
lists = [[1, 4, 5], [1, 3, 4], [2, 6]]
merged_list = merge_k_lists(lists)
print("Відсортований список:", merged_list)
