import multiprocessing
import time

n = 10000000000000
processes_num = 8  # количество процессов


def calculate_partial_sum(start: int, end: int, result_queue: multiprocessing.Queue):
    """Вычисляет сумму чисел в диапазоне и кладёт результат в очередь"""
    total_sum = (start + end) * (end - start + 1) // 2
    result_queue.put(total_sum)
    print(f"Процесс {multiprocessing.current_process().name}: "
          f"диапазон {start}-{end}, сумма = {total_sum}")


def main():

    chunk_size = n // processes_num
    processes = []
    result_queue = multiprocessing.Queue()

    start_time = time.time()

    # Создаём и запускаем процессы
    for i in range(processes_num):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < processes_num - 1 else n
        process = multiprocessing.Process(
            target=calculate_partial_sum,
            args=(start, end, result_queue)
        )
        processes.append(process)
        process.start()

    # Ждём завершения всех процессов
    for process in processes:
        process.join()

    # Собираем результаты из очереди
    total_sum = 0
    while not result_queue.empty():
        total_sum += result_queue.get()

    end_time = time.time()

    print(f"\nРезультат: {total_sum}")
    print(f"Время выполнения: {end_time - start_time:.4f} секунд")


if __name__ == "__main__":
    main()