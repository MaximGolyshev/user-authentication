import hashlib
import io
import struct


class HashCode:
    # задаем значения по умолчанию для параметров класса
    hash_name = 'sha512_256'
    iterations = 4096
    key_len = 16
    bytes_value = None
    hex_value = None

    # метод для генерации хеш-кода на основе пароля и соли
    def __new__(cls, *, password: str, salt: str):
        # преобразуем пароль и соль в байтовые строки
        password_bytes = password.encode('utf-8')
        salt_salt = salt.encode('utf-8')
        # генерируем хеш-код на основе пароля и соли с помощью функции pbkdf2_hmac из модуля hashlib
        cls.bytes_value = hashlib.pbkdf2_hmac(
            hash_name=cls.hash_name,
            password=password_bytes,
            salt=salt_salt,
            iterations=cls.iterations,
            dklen=cls.key_len
        )

        # преобразуем байты хеш-кода в строку в шестнадцатеричном формате
        string_io = io.StringIO()
        for i in cls.bytes_value:
            a = struct.pack('B', i).hex()
            string_io.write(a)
        cls.hex_value = string_io.getvalue()

        # возвращаем строковое значение хеш-кода
        return cls.hex_value
