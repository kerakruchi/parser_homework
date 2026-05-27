import os
import logging
import requests
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- ПАРСЕР ---
def fetch_homework():
    """
    Функция для получения домашних заданий.
    ВНИМАНИЕ: URL и заголовки нужно адаптировать под реальное API дневника.
    Вам нужно изучить сетевые запросы в браузере (F12 -> Network), 
    чтобы найти точный endpoint для домашнего задания.
    """
    # Пример эндпоинта (ЕГО НУЖНО ЗАМЕНИТЬ НА РЕАЛЬНЫЙ)
    url = "https://dnevnik2.petersburgedu.ru/api/journal/homework" 
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}", # Или используйте Cookie, если там куки
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    # Параметры запроса (например, дата)
    params = {
        "date_from": datetime.now().strftime("%Y-%m-%d"),
        # "date_to": ...
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Здесь нужно парсить JSON. Структура зависит от ответа сервера.
        # Ниже представлен псевдокод парсинга:
        homeworks = []
        for item in data.get("items", []):
            subject = item.get("subject_name", "Неизвестный предмет")
            task = item.get("description", "Нет описания")
            date = item.get("date", "Не указана")
            homeworks.append(f"📚 <b>{subject}</b> ({date}):\n{task}\n")
        
        if not homeworks:
            return "🎉 На сегодня домашних заданий нет (или не удалось их найти)!"
        
        return "📝 <b>Домашние задания:</b>\n\n" + "\n".join(homeworks)

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к дневнику: {e}")
        return "❌ Не удалось получить данные с дневника. Возможно, истек токен авторизации."


# --- РАСПИСАНИЕ ---
async def scheduled_send_homework():
    """Функция, которая будет вызываться по расписанию"""
    logging.info("Запуск проверки домашних заданий по расписанию...")
    message_text = fetch_homework()
    await bot.send_message(chat_id=CHAT_ID, text=message_text)


# --- ХЭНДЛЕРЫ БОТА ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для парсинга домашки. Напиши /homework, чтобы получить задания прямо сейчас.")

@dp.message(Command("homework"))
async def cmd_homework(message: types.Message):
    await message.answer("Ищу домашние задания...")
    message_text = fetch_homework()
    await message.answer(message_text)


# --- ЗАПУСК ---
async def main():
    # Настройка планировщика (каждый день в 15:00 по Москве)
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(scheduled_send_homework, 'cron', hour=15, minute=0)
    scheduler.start()

    logging.info("Бот запущен!")
    
    # Запуск поллинга
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
