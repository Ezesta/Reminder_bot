import logging
import os.path
import sqlite3
import uuid
from datetime import datetime, timedelta
from pprint import pprint
from typing import Union, NamedTuple

from Bot.ReminderBot.config.config_reader import load_config

config = load_config(r'/home/artem/PycharmProjects/Pt9/ReminderBot/config/config.ini')


class Remind(NamedTuple):
    user_id: int
    name: str
    text: str


class SQLiteDB:
    def __init__(self):
        self.connection = sqlite3.connect(r'users.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self._create_table_users()

    def _create_table_users(self):
        """Создает таблицу напоминаний

        :return:
        """
        with self.connection:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS users"
                                "("
                                "id TEXT UNIQUE,"
                                "user_id INTEGER,"
                                "name TEXT,"
                                "date TEXT,"
                                "text TEXT"
                                ")")

    def insert_one_value(self, user_id: int, name: str, date: str, text: str, _id=None) -> Union[bool, int, tuple]:
        """Вставка напоминания в БД

        :param user_id: id пользователя в телеграм
        :param name: имя пользователя в телеграм
        :param date: дата, в которую должно прийти напоминание
        :param text: текст напоминания
        :param _id: уникальный id записи в БД
        :return: bool, status code, ответ в виде текста или обновления
        """
        try:
            if not _id:
                value = (str(uuid.uuid4()), user_id, name, date, text)
            else:
                value = (user_id, name, date, text)
            if not self._check_duplicates(value):
                with self.connection:
                    self.cursor.execute(
                        "INSERT INTO users (id, user_id, name, date, text) VALUES (?, ?, ?, ?, ?)", value
                    )
                    return True, 200, value
            else:
                return False, 404, value

        except Exception as ex:
            logging.error(f'{repr(ex)}')
            return False, 404, f'{repr(ex)}'

    def _check_duplicates(self, value: tuple) -> bool:
        """Проверка на дубликаты

        :param value: кортеж значений
        :return: bool
        """
        with self.connection:
            all_data = self.cursor.execute("SELECT user_id, name, date, text FROM users")
            for remind in all_data.fetchall():
                if remind == value[1:]:
                    return True

    def get_all_values_json(self):
        """Получение всех значений из базы данных

        :return:
        """
        try:
            with self.connection:
                all_data = self.cursor.execute("SELECT * FROM users")
                all_posts = self._get_formatted_json(all_data.fetchall())
                return all_posts, 200
        except Exception as ex:
            logging.error(f'{repr(ex)}')
            return repr(ex), 404

    def _get_formatted_json(self, users: Union[list, tuple]):
        """Возвращает данные в формате JSON

        :param users: все пользовательские записи в БД
        :return: JSON объект всех записей из БД
        """
        all_posts = dict()
        for user in users:
            _id = user[0]
            user_id = user[1]
            name = user[2]
            date = user[3]
            text = user[4]
            all_posts[_id] = {
                'user_id': user_id,
                'name': name,
                'date': date,
                'text': text
            }
        return all_posts

    def delete_all_values(self):
        """Удаление всех значений из базы данных

        :return: сообщение об успехе или об ошибке, status code
        """
        with self.connection:
            try:
                self.cursor.execute('DELETE FROM users')
                return 'Все значения удалены', 200
            except Exception as ex:
                logging.error(f'{repr(ex)}')
                return repr(ex), 404

    def send_remind(self):
        """Отправка напоминания

        :return: user_id, name, text
        """
        with self.connection:
            time_direction = config.tg_bot.TIME_DIRECTION
            now = datetime.now() + timedelta(hours=time_direction)
            now_date = now.strftime('%H:%M - %d.%m.%Y')
            result = self.cursor.execute("SELECT * FROM users WHERE date = ?", (now_date,))

            all_data = result.fetchall()
            if all_data:
                all_id = tuple(
                    [_id[0] for _id in all_data]
                )
                self._delete_values(all_id)
                for value in all_data:
                    user_id = value[1]
                    name = value[2]
                    text = value[-1]
                    yield Remind(user_id, name, text)
            else:
                return

    def _delete_values(self, all_id: tuple):
        """Удаление значений по id

        :param all_id: кортеж с id
        :return:
        """
        with self.connection:
            for _id in all_id:
                self.cursor.execute("DELETE FROM users WHERE id = ?", (_id,))


    @staticmethod
    def delete_db(db_file: str):
        """Удаляет базу данных


        :param db_file: путь к файлу базы данных
        :return:
        """
        if os.path.exists(db_file):
            os.remove(db_file)
            logging.warning('The database file been removed')
        else:
            logging.warning('Database fiel not exists')
