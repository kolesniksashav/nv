import time
from queue import Queue

# Створення черги заявок
request_queue = Queue()
request_id = 0


def generate_request():
    # Генерує нову заявку з унікальним номером та додає її в чергу.
    global request_id
    request_id += 1
    request = f"Request-{request_id}"
    request_queue.put(request)
    print(f"Generated: {request}")


def process_request():
    # Обробляє наступну заявку, якщо вона є.
    if not request_queue.empty():
        request = request_queue.get()
        print(f"Processed: {request}")
    else:
        print("Queue is empty — nothing to process.")


def main():
    print("Service center started. Press Ctrl+C to stop.")
    try:
        while True:
            generate_request()
            process_request()
            time.sleep(1)  # Імітація часу роботи
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")


if __name__ == "__main__":
    main()
