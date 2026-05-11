import threading
import time

n = 10000000000000
threads_num = 8  # количество потоков


def calculate_sum(start: int, end: int, result: list, index: int):
    """Вычисляет сумму чисел с помощью арифметической прогрессии"""
    total_sum = (start + end) * (end - start + 1) // 2
    result[index] = total_sum
    print(f"Поток {index}: обработал диапазон {start}-{end}, сумма = {total_sum}")


def main():

    # Разбиваем общую задачу на части
    chunk_size = n // threads_num
    threads = []
    results = [0] * threads_num

    start_time = time.time()

    # Создаём и запускаем потоки
    for i in range(threads_num):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < threads_num - 1 else n
        thread = threading.Thread(
            target=calculate_sum,
            args=(start, end, results, i)
        )
        threads.append(thread)
        thread.start()

    # Ждём завершения всех потоков
    for thread in threads:
        thread.join()

    # Суммируем результаты
    total_sum = sum(results)
    end_time = time.time()

    print(f"\nРезультат: {total_sum}")
    print(f"Время выполнения: {end_time - start_time:.4f} сек")


if __name__ == "__main__":
    main()