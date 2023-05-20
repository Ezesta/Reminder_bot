import asyncio
import logging

from aiogram import types, Dispatcher, Bot
from aiogram.types import BotCommand
from aiogram.utils.exceptions import BadRequest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette import status

from Bot.ReminderBot.bot_config import dp, bot, TOKEN, logger, config, DB
from Bot.ReminderBot.schedule import scheduler

app = FastAPI()
WEBHOOK_PATH = f'/bot/{TOKEN}'
WEBHOOK_URL = config.tg_bot.HOST_URL + WEBHOOK_PATH

print(WEBHOOK_URL)


async def set_commands(bot: Bot):
    """Установка команд для бота

    :param bot:
    :return:
    """
    commands = [
        BotCommand(command='/start', description='Начало работы'),
        BotCommand(command='/cancel', description='Отмена'),
        BotCommand(command='/bug_report', description='Отправить сообщение об ошибке'),
    ]

    await bot.set_my_commands(commands)


async def bot_main():
    """Применение настроек бота

    :return:
    """
    from Bot.ReminderBot.handlers import other, bug_report, reminder

    logging.info('Bot started')

    bug_report(dp)
    other(dp)
    reminder(dp)

    await set_commands(bot)


@app.on_event('startup')
async def on_startup():
    """
    Установка вебхука
    :return:
    """
    try:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(
                url=WEBHOOK_URL,
                drop_pending_updates=True
            )
        asyncio.create_task(scheduler())
    except BadRequest as ex:
        if 'ip address 127.0.0.1 is reserved' in str(ex):
            logging.error('ip address 127.0.0.1 is reserved')
        else:
            logging.error(repr(ex))


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    """Получение обновлений Telegram

    :param update: Telegram update
    :return:
    """
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await bot_main()
    await dp.process_update(telegram_update)


@app.on_event('shutdown')
async def on_shutdown():
    """
    Закрытие сессии и удаление вебхука
    :return:
    """
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()
    await bot.delete_webhook()


@app.get('/')
async def home():
    """
    Домашняя страница
    :return:
    """
    return 'Бот запущен'


@app.get(f'{WEBHOOK_PATH}/info')
async def info():
    """
    Получение всей информации из базы данных
    :return: JSON Response
    """
    response = DB.get_all_values_json()
    if response[1] == status.HTTP_200_OK:
        return JSONResponse(
            content=response[0],
            status_code=status.HTTP_200_OK,
            media_type='application/json'
        )
    else:
        response = {'detail': 'NOT FOUND'}
        return JSONResponse(
            content=response,
            status_code=status.HTTP_404_NOT_FOUND,
            media_type='application/json'
        )


@app.get(f'{WEBHOOK_PATH}/clear')
async def clear_db():
    """
    Удаление всех значений из базы данных
    :return: JSON Response
    """
    response = DB.delete_all_values()
    if response[1] == status.HTTP_200_OK:
        response = {
            'detail': 'all data cleaned'
        }
        return JSONResponse(
            content=response,
            status_code=status.HTTP_200_OK,
            media_type='application/json'
        )


@app.post(f'{WEBHOOK_PATH}/post/')
async def add_remind(remind: dict):
    """Добавление пользователя в базу данных

    :param remind: Напоминание
    :return: JSON Response
    """
    user_id = remind['user_id']
    name = remind['name']
    date = remind['date']
    text = remind['text']

    response = DB.insert_one_value(user_id, name, date, text)
    if response[1] == status.HTTP_200_OK:
        return JSONResponse(
            content=response[2],
            status_code=status.HTTP_201_CREATED,
            media_type='application/json'
        )
    else:
        response = {'detail': 'NOT FOUND'}
        return JSONResponse(
            content=response,
            status_code=status.HTTP_404_NOT_FOUND,
            media_type='application/json'
        )
