import os
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
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
    """
    # ⚠️ ВАЖНО: Вам нужно подставить реальный URL из вкладки Network!
    # Я пишу примерный. Как найдете запрос в Network (шаг 5 выше), 
    # скопируйте "Request URL" и вставьте сюда.
    url = "https://dnevnik2.petersburgedu.ru/api/journal/homework" 
    
    # Формируем заголовки. Если вы скопировали Bearer токен:
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    # Если в шаге 6 вы нашли только Cookie, а не Authorization, 
    # раскомментируйте строку ниже и удалите строку Authorization выше:
    # headers["Cookie"] = AUTH_TOKEN

    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Если сайт отвечает ошибкой (например, 401 Unauthorized - значит токен устарел)
        if response.status_code != 200:
            logging.error(f"Ошибка API: {response.status_code} - {response.text}")
            return f"❌ Сайт вернул ошибку {response.status_code}. Возможно, токен устарел."

        data = response.json()
        
        # ⚠️ ВАЖНО: Эта часть требует адаптации!
        # Откройте Request URL в браузере (там будет JSON текст).
        # Посмотрите, как называются поля (например, data, items, subject, text и т.д.)
        # И измените код ниже под вашу структуру.
        homeworks = []
        
        # ПРИМЕР ПАРСИНГА (замените ключи на реальные):
        for item in data.get("items", []):
            subject = item.get("subject_name", "Предмет")
            task = item.get("description", "Нет описания")
            homeworks.append(f"📚 <b>{subject}</b>:\n{task}\n")
        
        if not homeworks:
            return "🎉 На ближайшие дни домашних заданий нет!"
        
        return "📝 <b>Домашние задания:</b>\n\n" + "\n".join(homeworks)

    except Exception as e:
        logging.error(f"Ошибка при запросе: {e}")
        return "❌ Произошла ошибка при подключении к дневнику."


# --- ХЭНДЛЕРЫ БОТА ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! 👋\n"
        "Напиши /homework, и я попробую достать твои домашние задания из дневника."
    )

@dp.message(Command("homework"))
async def cmd_homework(message: types.Message):
    # Чтобы пользователь не ждал в пустую, отправляем реакцию
    wait_msg = await message.answer("⏳ Ищу домашние задания...") 
    
    # Получаем данные
    result_text = fetch_homework()
    
    # Редактируем сообщение с ожиданием на результат
    await wait_msg.edit_text(result_text)


# --- ЗАПУСК ---
async def main():
    logging.info("Бот запущен! Иду в Telegram...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
