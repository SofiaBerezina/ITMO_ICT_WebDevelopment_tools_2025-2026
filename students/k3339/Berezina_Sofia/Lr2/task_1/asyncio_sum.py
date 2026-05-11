import asyncio
import time

n = 10000000000000
tasks_num = 8  # количество асинхронных задач


async def calculate_partial_sum(start: int, end: int, task_id: int) -> int:
    """Асинхронно вычисляет сумму"""

    partial_sum = end - start + 1
    total_sum = (start + end) * partial_sum // 2
    print(f"Задача {task_id}: обработала диапазон {start}-{end}")
    return total_sum


async def main_async():
    chunk_size = n // tasks_num
    tasks = []

    for i in range(tasks_num):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < tasks_num - 1 else n
        tasks.append(calculate_partial_sum(start, end, i))

    # Запускаем все задачи параллельно
    results = await asyncio.gather(*tasks)
    return sum(results)


def main():

    start_time = time.time()
    total_sum = asyncio.run(main_async())
    end_time = time.time()

    print(f"\nРезультат: {total_sum}")
    print(f"Время выполнения: {end_time - start_time:.4f} секунд")


if __name__ == "__main__":
    main()