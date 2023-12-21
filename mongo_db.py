from __future__ import annotations

from typing import Any, Mapping
from pymongo import MongoClient
from pymongo.cursor import Cursor


class MongoDB(object):
    def __init__(self, *, host: str, port: int, db_name: str, collection: str):
        # Создать экземпляр класса MongoClient для подключения к базе данных
        self._client = MongoClient(f'mongodb://{host}:{port}')
        # Выбрать коллекцию в базе данных
        self._collection = self._client[db_name][collection]

    # Определить метод create_user для добавления нового пользователя в базу данных
    def create_user(self, *, data: dict) -> bool:
        try:
            # Проверить, существует ли пользователь с таким же именем
            if self._collection.find_one({'username': data.get('username')}) is None:
                # Если пользователь не существует, добавить его в базу данных
                self._collection.insert_one(data)
            else:
                raise Exception(f"Пользователь {data.get('username')} уже существует!")
        except Exception as ex:
            print('[create_user] Ошибка!')
            print(ex)
            return False
        else:
            print(f"[create_user] Новый пользователь {data.get('username')}!")
            return True

    # Определить метод get_all_users для получения всех пользователей из базы данных
    def get_all_users(self) -> Cursor[Mapping[str, Any] | Any] | None:
        try:
            # Получить все данные из коллекции
            data = self._collection.find()
        except Exception as ex:
            print('[get_all] Ошибка!')
            print(ex)
        else:
            print('[get_all] Получили всех пользователей!')
            return data

    # Определить метод find_first для поиска первого пользователя, удовлетворяющего заданному фильтру
    def find_first(self, *, filt: dict) -> Cursor[Mapping[str, Any] | Any] | None:
        try:
            # Найти первого пользователя, удовлетворяющего заданному фильтру
            data = self._collection.find_one(filt)
        except Exception as ex:
            print('[find_by_username] Ошибка!')
            print(ex)
        else:
            print(f'[find_by_username] Получили пользователя по ключу!')
            return data

    # Определить метод change_user для обновления данных пользователя в базе данных
    def change_user(self, *, filt: dict, update: dict) -> bool:
        try:
            # Проверить, существует ли пользователь с заданным фильтром
            if self._collection.find_one(filt) is not None:
                # Если пользователь существует, обновить его данные
                self._collection.update_one(filt, {'$set': update})
            else:
                raise Exception(f'Пользователь с заданным фильтром не найден!')
        except Exception as ex:
            print('[change_user] Ошибка!')
            print(ex)
            return False
        else:
            print(f'[change_user] Пользователь с заданным фильтром обновлён!')
            return True

    # Определить метод delete_user для удаления пользователя из базы данных
    def delete_user(self, *, filt: dict):
        try:
            # Проверить, существует ли пользователь с заданным фильтром
            if self._collection.find_one(filt) is not None:
                # Если пользователь существует, удалить его из базы данных
                self._collection.delete_one(filt)
            else:
                raise Exception(f'Пользователь не найден!')
        except Exception as ex:
            print('[delete_user] Ошибка!')
            print(ex)
            return False
        else:
            print(f'[delete_user] Пользователь удалён!')

    @property
    def client(self):
        return self.client
