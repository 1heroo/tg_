import logging
import asyncio
import sys
from io import BytesIO

import pandas as pd
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InputFile, FSInputFile, BufferedInputFile

from app.services import Services

TOKEN = '6355925335:AAFufqe03Hm90KXe1MyxZf4jQiFzrtsfk6Y'


dp = Dispatcher()
bot = Bot(token=TOKEN)

services = Services()


async def send_message_b_link(message: Message):
    text = 'Введите ссылку на категорию'
    await message.answer(
        text=text
    )


async def main() -> None:
    await bot.delete_webhook()

    await dp.start_polling(bot)


@dp.message(CommandStart())
async def start(message: Message):
    await send_message_b_link(message=message)


@dp.message()
async def message_handler(message: Message):
    link = message.text

    if link and not link.startswith('https://'):
        await message.answer('Введите корректную ссылку')
        return

    await message.answer('Ожидайте')
    data = await services.launch_parsing(link)
    df = pd.DataFrame(data)

    filename = 'dataframe.xlsx'
    df.to_excel(filename, index=False)
    await bot.send_document(chat_id=message.chat.id, document=BufferedInputFile.from_file(filename), reply_to_message_id=message.message_id)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
