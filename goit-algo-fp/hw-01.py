class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    # ---------- Базові операції ----------

    def insert_at_beginning(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def insert_at_end(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return

        cur = self.head
        while cur.next:
            cur = cur.next
        cur.next = new_node

    def delete_node(self, key: int):
        cur = self.head

        if cur and cur.data == key:
            self.head = cur.next
            return

        prev = None
        while cur and cur.data != key:
            prev = cur
            cur = cur.next

        if cur is None:
            return

        prev.next = cur.next

    def search_element(self, data: int):
        cur = self.head
        while cur:
            if cur.data == data:
                return cur
            cur = cur.next
        return None

    def print_list(self):
        cur = self.head
        while cur:
            print(cur.data, end=" -> ")
            cur = cur.next
        print("None")

    # ---------- 1. Реверсування списку ----------

    def reverse(self):
        prev = None
        current = self.head

        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node

        self.head = prev

    # ---------- 2. Сортування (Merge Sort) ----------

    def sort(self):
        self.head = self._merge_sort(self.head)

    def _merge_sort(self, head):
        if head is None or head.next is None:
            return head

        middle = self._get_middle(head)
        next_to_middle = middle.next
        middle.next = None

        left = self._merge_sort(head)
        right = self._merge_sort(next_to_middle)

        return self._sorted_merge(left, right)

    def _get_middle(self, head):
        slow = head
        fast = head

        while fast.next and fast.next.next:
            slow = slow.next
            fast = fast.next.next

        return slow

    @staticmethod
    def _sorted_merge(a, b):
        if not a:
            return b
        if not b:
            return a

        if a.data <= b.data:
            result = a
            result.next = LinkedList._sorted_merge(a.next, b)
        else:
            result = b
            result.next = LinkedList._sorted_merge(a, b.next)

        return result

    # ---------- 3. Об’єднання двох відсортованих списків ----------

    @staticmethod
    def merge_sorted_lists(list1, list2):
        merged = LinkedList()
        merged.head = LinkedList._sorted_merge(list1.head, list2.head)
        return merged


# ================== DEMO ==================

if __name__ == "__main__":
    llist = LinkedList()

    llist.insert_at_end(5)
    llist.insert_at_end(20)
    llist.insert_at_end(10)
    llist.insert_at_end(25)
    llist.insert_at_end(15)

    print("Початковий список:")
    llist.print_list()

    print("\nРеверсований список:")
    llist.reverse()
    llist.print_list()

    print("\nВідсортований список:")
    llist.sort()
    llist.print_list()

    # Другий відсортований список
    llist2 = LinkedList()
    llist2.insert_at_end(3)
    llist2.insert_at_end(8)
    llist2.insert_at_end(17)
    llist2.insert_at_end(30)

    print("\nДругий відсортований список:")
    llist2.print_list()

    print("\nОб'єднаний відсортований список:")
    merged = LinkedList.merge_sorted_lists(llist, llist2)
    merged.print_list()
