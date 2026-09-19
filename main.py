import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from PIL import Image, ImageDraw, ImageFont
import io
import asyncio

TOKEN = os.getenv("8233218434:AAHnwMVmY0LTiTkYsx6DVEHJvjEPo7moezc")
bot = Bot(token=TOKEN)
dp = Dispatcher(

@dp.message(Command("score"))
async def send_match_banner(message: types.Message):
  # 1. Открываем ваш красивый пустой шаблон
  # (Убедитесь, что файл template.png лежит в той же папке)
  img = Image.open("template.png")
  draw = ImageDraw.Draw(img)
  
  # 2. Загружаем шрифт (нужно скачать любой .ttf файл и положить рядом)
  # 60 - это размер шрифта
  try:
      font = ImageFont.truetype("arial.ttf", 60)
  except IOError:
      font = ImageFont.load_default() # Резервный шрифт, если arial.ttf нет

  # 3. Данные для баннера (в будущем они будут приходить от API)
  team1 = "ФК Челябинск"
  team2 = "Волга"
  score = "1 : 0"

  # 4. Наносим текст на изображение (координаты X, Y)
  # Координаты нужно будет подобрать методом тыка под ваш дизайн
  draw.text((100, 200), team1, font=font, fill="white")
  draw.text((400, 200), score, font=font, fill="#e53935") # Красный цвет для счета
  draw.text((600, 200), team2, font=font, fill="white")

  # 5. Сохраняем картинку в буфер (оперативную память), чтобы не плодить файлы
  image_buffer = io.BytesIO()
  img.save(image_buffer, format="PNG")
  image_buffer.seek(0)

  # 6. Упаковываем для aiogram и отправляем
  photo = BufferedInputFile(image_buffer.read(), filename="banner.png")

  await message.answer_photo(
      photo=photo, 
      caption="🔥 <b>Гол!</b>\nСчет изменился.", 
      parse_mode="HTML"
  )
# Функция-заглушка, которая отвечает Render, что бот жив
async def handle_ping(request):
    return web.Response(text="Bot is alive!")

async def main():
    # Создаем фейковый веб-сервер
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render автоматически передает нужный порт через переменную окружения PORT
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    # Запускаем поллинг Telegram-бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
