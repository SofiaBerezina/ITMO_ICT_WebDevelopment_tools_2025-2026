import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import select
from connection import get_session, init_db
from models import Task, Priority, Status, TaskType
import time

URLS = [
    "http://www.python.org",
    "http://www.github.com",
    "http://www.stackoverflow.com",
]


async def parse_and_save(url):
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, timeout=10) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.find('title')
                title_text = title.text.strip() if title else "No title"

                # Сохраняем в БД
                def save():
                    with next(get_session()) as db:
                        priority = db.exec(select(Priority).where(Priority.name == "medium")).first()
                        status = db.exec(select(Status).where(Status.name == "pending")).first()
                        task_type = db.exec(select(TaskType).where(TaskType.name == "work")).first()

                        task = Task(
                            title=f"Прочитать: {title_text[:50]}",
                            description=f"Спарсено с {url}",
                            priority_id=priority.id,
                            status_id=status.id,
                            task_type_id=task_type.id,
                            user_id=1
                        )
                        db.add(task)
                        db.commit()
                        print(f"Сохранено: {url}")

                await asyncio.to_thread(save)
    except Exception as e:
        print(f"Ошибка {url}: {e}")


async def main_async():
    tasks = [parse_and_save(url) for url in URLS]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    init_db()
    start = time.time()
    asyncio.run(main_async())
    print(f"Время: {time.time() - start:.2f} сек")