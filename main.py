import os
import io
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from PIL import Image, ImageDraw, ImageFont

# Включаем логирование, чтобы видеть все процессы в Render
logging.basicConfig(level=logging.INFO)

# 1. Безопасно получаем токен
TOKEN = os.getenv("BOT_TOKEN")

# СПЕЦИАЛЬНАЯ ПРОВЕРКА: Если Render не передал токен, скрипт остановится и напишет почему
if not TOKEN:
  raise ValueError("ОШИБКА: Переменная BOT_TOKEN пустая! Проверьте настройки Environment Variables в Render.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 2. Обработчик команды /score (генерация картинки)
@dp.message(Command("score"))
async def send_match_banner(message: types.Message):
  try:
      # Открываем шаблон (убедитесь, что template.png загружен на GitHub)
      img = Image.open("template.png")
      draw = ImageDraw.Draw(img)
    
      # Загружаем шрифт (убедитесь, что arial.ttf загружен на GitHub)
      try:
          font = ImageFont.truetype("arial.ttf", 60)
      except IOError:
          font = ImageFont.load_default() # Резервный шрифт, если arial.ttf не найден

      # Данные матча
      team1 = "ФК Челябинск"
      team2 = "Волга"
      score = "1 : 0"
    
      # Рисуем текст (координаты X, Y)
      draw.text((100, 200), team1, font=font, fill="white")
      draw.text((400, 200), score, font=font, fill="#e53935") 
      draw.text((600, 200), team2, font=font, fill="white")

      # Сохраняем картинку в оперативную память
      image_buffer = io.BytesIO()
      img.save(image_buffer, format="PNG")
      image_buffer.seek(0)
    
      # Отправляем в чат Telegram
      photo = BufferedInputFile(image_buffer.read(), filename="banner.png")
      await message.answer_photo(
          photo=photo, 
          caption="🔥 <b>Гол!</b>\nСчет изменился.", 
          parse_mode="HTML"
      )
  except Exception as e:
      # Если картинка или шрифт не найдены, бот пришлет ошибку прямо в чат
      await message.answer(f"Произошла ошибка при генерации: {e}")

# 3. Функция-заглушка для Render (чтобы он не отключал бота)
async def handle_ping(request): return web.Response(text="Bot is alive!")
  
# 4. Главная функция запуска
async def main():
  # Настраиваем фейковый веб-сервер
  app = web.Application()
  app.router.add_get('/', handle_ping)
  runner = web.AppRunner(app)
  await runner.setup()

  # Забираем порт, который выдаст Render
  port = int(os.environ.get("PORT", 10000))
  site = web.TCPSite(runner, '0.0.0.0', port)
  await site.start()

  logging.info(f"Веб-сервер успешно запущен на порту {port}")

  # Запускаем самого бота
  await bot.delete_webhook(drop_pending_updates=True)
  logging.info("Telegram-бот начал работу! Жду сообщений...")
  await dp.start_polling(bot)

if name == "main":
  asyncio.run(main())
