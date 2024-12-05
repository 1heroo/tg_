import logging
import asyncio
import sys
from io import BytesIO

import pandas as pd
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InputFile, FSInputFile, BufferedInputFile

from app.services import Services


TOKEN = '2069735092:AAFybLlvXLHi1-OO2YOau99SKW6nWPECC4I'


dp = Dispatcher()
bot = Bot(token=TOKEN)

services = Services()
working = False


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
    global working

    if working:
        await message.answer('Сейчас обрабтывается категория, ожидайте')
        return

    try:
        link = message.text

        if link and not link.startswith('https://'):
            await message.answer('Введите корректную ссылку')
            return

        await message.answer('Ожидайте')
        working = True

        data = await services.launch_parsing(link)
        df = pd.DataFrame(data)

        filename = 'dataframe.xlsx'
        df.to_excel(filename, index=False)
        await bot.send_document(chat_id=message.chat.id, document=BufferedInputFile.from_file(filename),
                                reply_to_message_id=message.message_id)

        working = False
    except Exception as e:
        await message.answer(f'Ошибка {e}, попробуйте снова ')
        working = False


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
