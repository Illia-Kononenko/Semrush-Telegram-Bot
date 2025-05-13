import requests
from datetime import datetime
import schedule
import time
import pytz
import os
import json
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Часовой пояс Киева
kyiv_tz = pytz.timezone("Europe/Kyiv")

# Переменные окружения
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_ids_raw = os.getenv("TELEGRAM_CHAT_IDS")  # Пример: -1001234567890,-1009876543210

# Проверка наличия переменных окружения
if not bot_token:
    raise ValueError("Переменная окружения TELEGRAM_BOT_TOKEN не задана")
if not chat_ids_raw:
    raise ValueError("Переменная окружения TELEGRAM_CHAT_IDS не задана")

# Преобразование строки chat_id в список
chat_ids = [chat_id.strip() for chat_id in chat_ids_raw.split(",")]

# Ссылки на изображения
urls = [
    "https://www.semrush.com/sensor/static/widget/data/mobile-us/widget.large.png",
    "https://www.semrush.com/sensor/static/widget/data/us/widget.large.png"
]

def job():
    try:
        print("Запуск задачи:", datetime.now(kyiv_tz).strftime("%Y-%m-%d %H:%M:%S"))

        # Скачиваем изображения
        for index, url_img in enumerate(urls, 1):
            response = requests.get(url_img)
            if response.status_code == 200:
                with open(f"image{index}.png", "wb") as file:
                    file.write(response.content)
            else:
                print(f"Ошибка загрузки изображения {index}")
                return

        # Дата для подписи
        current_date = datetime.now(kyiv_tz).strftime("%d.%m.%Y")

        # Открываем изображения один раз
        with open("image1.png", "rb") as img1, open("image2.png", "rb") as img2:
            media_payload = json.dumps([
                {
                    "type": "photo",
                    "media": "attach://photo1",
                    "caption": current_date
                },
                {
                    "type": "photo",
                    "media": "attach://photo2"
                }
            ])

            # Отправляем в каждый чат
            for chat_id in chat_ids:
                url = f'https://api.telegram.org/bot{bot_token}/sendMediaGroup'
                files = {
                    "media": (None, media_payload),
                    "photo1": img1,
                    "photo2": img2
                }
                response = requests.post(url, data={"chat_id": chat_id}, files=files)

                if response.status_code == 200:
                    print(f"Фото отправлены в чат {chat_id}")
                else:
                    print(f"Ошибка отправки в чат {chat_id}: {response.status_code} — {response.text}")

    except Exception as e:
        print("Произошла ошибка в задаче:", e)

    finally:
        # Удаление временных файлов
        for i in range(1, 3):
            try:
                os.remove(f"image{i}.png")
            except FileNotFoundError:
                pass

def schedule_job():
    schedule.every().monday.at("13:30").do(job)
    schedule.every().tuesday.at("13:30").do(job)
    schedule.every().wednesday.at("13:30").do(job)
    schedule.every().thursday.at("13:30").do(job)
    schedule.every().friday.at("13:30").do(job)

    print("Планировщик запущен. Ожидание задач...")

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    if "--test" in sys.argv:
        job()
    else:
        schedule_job()
