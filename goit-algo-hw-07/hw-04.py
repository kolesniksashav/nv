class Comment:
    DELETED_TEXT = "Цей коментар було видалено."

    def __init__(self, text: str, author: str):
        self.text = text           # текст коментаря
        self.author = author       # автор
        self.replies = []          # список відповідей (Comment)
        self.is_deleted = False    # прапорець "видалено"

    def add_reply(self, reply: "Comment") -> None:
        # Додає відповідь до поточного коментаря. 
        self.replies.append(reply)

    def remove_reply(self) -> None:
        # "Видаляє" коментар: не прибирає з дерева, а замінює текст і ставить прапорець is_deleted.
        self.text = self.DELETED_TEXT
        self.is_deleted = True

    def display(self, level: int = 0) -> None:
        # Рекурсивно виводить коментар і всі відповіді. Відступ — 4 пробіли на кожен рівень вкладеності.
        indent = " " * 4 * level

        if self.is_deleted:
            print(f"{indent}{self.DELETED_TEXT}")
        else:
            print(f"{indent}{self.author}: {self.text}")

        for reply in self.replies:
            reply.display(level + 1)


# ---- Приклад з умови ----
root_comment = Comment("Яка чудова книга!", "Бодя")
reply1 = Comment("Книга повне розчарування :(", "Андрій")
reply2 = Comment("Що в ній чудового?", "Марина")

root_comment.add_reply(reply1)
root_comment.add_reply(reply2)

reply1_1 = Comment("Не книжка, а перевели купу паперу ні нащо...", "Сергій")
reply1.add_reply(reply1_1)

reply1.remove_reply()
root_comment.display()

