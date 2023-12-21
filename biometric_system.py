from datetime import datetime, timedelta
import numpy as np
from bson import json_util
from pydantic import ValidationError
from src.db.hash_code import HashCode
from src.db.mongo_db import MongoDB
from src.db.schema import UserValidator
from src.utils.math_module import hamming_mera, hamming_distance, averaging_value


class BiometricSystem:
    def __init__(self, *,
                 host: str = 'localhost',
                 port: int = 27017,
                 db_name: str = 'example',
                 collection: str = 'User'):
        # Установить значение по умолчанию для expiring равным 180 дням
        self.expiring: int = 180
        # Создать экземпляр класса MongoDB
        self._db = MongoDB(host=host, port=port, db_name=db_name, collection=collection)

    # Определить метод register_user для регистрации нового пользователя
    def register_user(self, *, data: dict) -> bool:
        # Получить текущую дату и время
        registered_at = datetime.now()
        # Рассчитать дату истечения срока действия на основе текущей даты и времени и значения expiring
        expired_at = registered_at + timedelta(days=self.expiring)

        # Сгенерировать хэш-код для пароля с помощью класса HashCode
        password = data['password']
        password = HashCode(password=password, salt=registered_at.strftime('%Y-%m-%d'))

        # Рассчитать средние интервалы и расстояние от средних интервалов
        mu_intervals = averaging_value(data['intervals'])
        dm_intervals = []
        for intervals in data['intervals']:
            dm_intervals.append(hamming_distance(intervals, mu_intervals))

        # Рассчитать среднее время удержания и расстояние от среднего времени удержания
        mu_holdings_time = averaging_value(data['holdings_time'])
        dm_holdings_time = []
        for holdings_time in data['holdings_time']:
            dm_holdings_time.append(hamming_distance(holdings_time, mu_holdings_time))

        # Создать словарь, содержащий все данные пользователя
        data = {'username': data['username'],
                'password': password,
                'registered_at': registered_at.date(),
                'expired_at': expired_at.date(),
                'mu_intervals': mu_intervals,
                'dm_intervals': dm_intervals,
                'mu_holdings_time': mu_holdings_time,
                'dm_holdings_time': dm_holdings_time}

        # Проверить данные пользователя с помощью схемы UserValidator
        try:
            UserValidator(**data)
        except ValidationError as ex:
            print('[register_user] Ошибка валидации!')
            print(ex)
            return False

        # Преобразовать объекты даты в формат ISO
        data['registered_at'] = data['registered_at'].isoformat()
        data['expired_at'] = data['expired_at'].isoformat()
        # Вызвать метод create_user класса MongoDB для вставки данных пользователя в базу данных
        return self.db.create_user(data=data)

    # Определить метод identify_user для идентификации пользователя
    def identify_user(self, *, data: dict) -> bool:
        try:
            # Найти данные пользователя в базе данных по имени пользователя
            cursor = self.db.find_first(filt={'username': data['username']})
            user_data = json_util.loads(json_util.dumps(cursor, indent=4))

            # Проверить, истек ли срок действия учетной записи пользователя
            if datetime.today() > datetime.fromisoformat(user_data['expired_at']):
                raise ValueError('Нужно обновить логин!')

            # Сгенерировать хэш-код для пароля с помощью класса HashCode и проверить, соответствует ли он сохраненному паролю
            password = HashCode(password=data['password'], salt=user_data['registered_at'])
            if password != user_data['password']:
                raise ValueError('Неверный пароль!')

            # Рассчитать нижнюю и верхнюю границы расстояния Хэмминга для интервалов и проверить, являются ли
            # интервалы пользователя типичными
            mu_intervals = user_data['mu_intervals']
            dm_intervals = user_data['dm_intervals']
            lower, upper = hamming_mera(dm_intervals)
            d_intervals = hamming_distance(data['intervals'], mu_intervals)
            if not (lower <= d_intervals <= upper):
                raise ValueError('Нетипичные интервалы в нажатии клавиш!')

            # # Рассчитать нижнюю и верхнюю границы расстояния Хэмминга для времени удержания и проверить, является ли
            # время удержания пользователя типичным
            mu_holdings_time = user_data['mu_holdings_time']
            dm_holdings_time = user_data['dm_holdings_time']
            lower, upper = hamming_mera(dm_holdings_time)
            d_holdings_time = hamming_distance(data['holdings_time'], mu_holdings_time)
            if not (lower <= d_holdings_time <= upper):
                raise ValueError('Нетипичное время удержания клавиш!')

        except Exception as ex:
            print('[identify_user] Ошибка идентификации!')
            print(ex)
            return False
        else:
            # Если успех, то рассчитываем новый эталон для пользователя и добавляет метрики
            mu_intervals = np.array(user_data['mu_intervals'])
            dm_intervals = list(user_data['dm_intervals'])

            mu_intervals = list((mu_intervals * len(dm_intervals) + np.array(data['intervals'])) /
                                len(dm_intervals) + 1)
            dm_intervals.append(d_intervals)

            mu_holdings_time = np.array(user_data['mu_holdings_time'])
            dm_holdings_time = list(user_data['dm_holdings_time'])

            mu_holdings_time = list((mu_holdings_time * len(dm_holdings_time) + np.array(data['holdings_time'])) /
                                    len(dm_holdings_time) + 1)
            dm_holdings_time.append(d_holdings_time)

            filt = {'username': user_data['username']}
            update = {'mu_intervals': mu_intervals,
                      'dm_intervals': dm_intervals,
                      'mu_holdings_time': mu_holdings_time,
                      'dm_holdings_time': dm_holdings_time}
            self.db.change_user(filt=filt, update=update)
            return True

    @property
    def db(self):
        return self._db

    @property
    def expiring(self):
        return self._expiring

    @expiring.setter
    def expiring(self, value: int):
        assert type(value) is int and value > 0
        self._expiring = value
