from src.db.biometric_system import BiometricSystem
from src.utils.keyboard_listener import collect_data_for_input

biometric_system = BiometricSystem()


def main():
    answer = ''
    while answer != 'q':
        print('Вы зарегистрированы? Ответьте (y - да, n - нет, q - выйти):')
        answer = input().strip().lower()
        if answer == 'y':
            username = input('Введите имя пользователя: ')
            print('Введите пароль: ')
            password, intervals, holdings_time = collect_data_for_input()

            biometric_system.identify_user(data={'username': username.strip(),
                                                 'password': password.strip(),
                                                 'intervals': intervals,
                                                 'holdings_time': holdings_time})
        elif answer == 'n':
            username = input('Введите имя пользователя: ')
            print('Введите пароль: ')
            password, intervals_i, holdings_time_i = collect_data_for_input()

            intervals = [intervals_i]
            holdings_time = [holdings_time_i]

            n = 5
            while n > 0:
                print(f'Повторите ещё {n} раз свой пароль: ')
                try:
                    password_i, intervals_i, holdings_time_i = collect_data_for_input()
                    if password.strip() == password_i.strip():
                        intervals.append(intervals_i)
                        holdings_time.append(holdings_time_i)
                        n -= 1
                    else:
                        raise ValueError('Пароли не совпадают!')
                except ValueError as e:
                    print(e)
                    continue

            # Создаем нового пользователя в базе данных
            biometric_system.register_user(data={'username': username.strip(),
                                                 'password': password.strip(),
                                                 'intervals': intervals,
                                                 'holdings_time': holdings_time})


if __name__ == '__main__':
    main()
