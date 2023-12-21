import random
from string import ascii_lowercase, ascii_uppercase, punctuation, digits
import unittest
import json
from src.db.biometric_system import BiometricSystem
from bson import json_util


# функция для генерации пароля заданной длины
def generate_password(length: int):
    alphabets = list(f'{ascii_lowercase}{ascii_uppercase}{digits}')
    return ''.join([random.choice(alphabets) for _ in range(length)])


# функция для генерации данных пользователей в формате JSON
def generate_users_to_json():
    users_data = []
    num_of_users = 5
    for i in range(num_of_users):
        password = generate_password(8)
        user_data = {}
        user_data.update({'username': f'test_{i}'})
        user_data.update({'password': password})
        attempts = 4
        # генерируем случайные интервалы между нажатиями клавиш и времена удерживания клавиш для каждой попытки
        user_data.update({'intervals':
                              [[random.normalvariate(0.5, 0.16) for _ in range(len(password) - 1)]
                               for _ in range(attempts)]})
        user_data.update({'holdings_time':
                              [[random.normalvariate(0.3, 0.05) for _ in range(len(password))]
                               for _ in range(attempts)]})
        users_data.append(user_data)
    # записываем данные пользователей в файл в формате JSON
    with open('test_users.json', 'w') as file:
        file.write(json.dumps(users_data, indent=4))


# класс для тестирования функционала биометрической системы
class TestTask(unittest.TestCase):
    def setUp(self):
        # создаем экземпляр биометрической системы для тестирования
        self.biometric_system = BiometricSystem(db_name='test')
        # генерируем данные пользователей и записываем их в файл
        generate_users_to_json()
        with open('test_users.json', 'rb') as f:
            self.users_data = json.load(f)

    # тест на регистрацию пользователей и их идентификацию
    def test_registration_and_identification(self):
        # регистрируем каждого пользователя и проверяем успешность операции
        for user_data in self.users_data:
            result = self.biometric_system.register_user(data=user_data)
            self.assertTrue(result)
            print(f'Пользователь {user_data["username"]} был зарегистрирован!\n')

        # для каждого пользователя проверяем, что его клавиатурный почерк определяется системой корректно
        for user_data in self.users_data:
            # Чтобы показать, что клавиатурный почерк подойдёт, если он принадлежит пользователю.
            intervals = user_data['intervals'][0]
            holdings_time = user_data['holdings_time'][0]

            # Чтобы показать, что не любой клавиатурный почерк подойдёт. Когда-то подойдёт, а когда - нет
            # intervals = [random.normalvariate(0.5, 0.12) for _ in range(len(user_data['password']) - 1)]
            # holdings_time = [random.normalvariate(0.3, 0.05) for _ in range(len(user_data['password']))]

            user = {'username': user_data['username'],
                    'password': user_data['password'],
                    'intervals': intervals,
                    'holdings_time': holdings_time}
            result = self.biometric_system.identify_user(data=user)
            self.assertTrue(result)
            print(f'Пользователь {user_data["username"]} зашёл в систему!\n')

        # получаем список всех пользователей из базы данных и записываем его в файл в формате JSON
        cursor = self.biometric_system.db.get_all_users()
        data = json_util.dumps(cursor, indent=4)
        with open('users_in_db.json', 'w') as file:
            file.write(data)

    def tearDown(self):
        # удаляем всех пользователей из базы данных после завершения тестов
        [self.biometric_system.db.delete_user(filt={'username': user['username']}) for user in self.users_data]


if __name__ == '__main__':
    unittest.main()
