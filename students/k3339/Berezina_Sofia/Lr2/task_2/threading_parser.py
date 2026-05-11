import threading
import requests
from bs4 import BeautifulSoup
from sqlmodel import select
from connection import get_session, init_db
from models import Task, Priority, Status, TaskType
import time

URLS = [
    "https://www.python.org",
    "https://www.github.com",
    "https://www.stackoverflow.com",
]

def parse_and_save(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title"

        with next(get_session()) as session:
            # Получаем ID справочников
            priority = session.exec(select(Priority).where(Priority.name == "medium")).first()
            status = session.exec(select(Status).where(Status.name == "pending")).first()
            task_type = session.exec(select(TaskType).where(TaskType.name == "work")).first()

            task = Task(
                title=f"Прочитать: {title_text[:50]}",
                description=f"Спарсено с {url}",
                priority_id=priority.id,
                status_id=status.id,
                task_type_id=task_type.id,
                user_id=1
            )
            session.add(task)
            session.commit()
            print(f"Сохранено: {url} -> {task.title}")
    except Exception as e:
        print(f"Ошибка {url}: {e}")


def main():
    init_db()

    threads = []
    for url in URLS:
        t = threading.Thread(target=parse_and_save, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Время: {time.time() - start:.2f} сек")