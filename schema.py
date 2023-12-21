import datetime
from string import ascii_lowercase, ascii_uppercase, punctuation, digits
from typing import Optional
from pydantic import BaseModel, validator, ValidationError


alphabets = ascii_lowercase, ascii_uppercase, punctuation, digits


class UserValidator(BaseModel):
    username: str
    password: str
    registered_at: Optional[datetime.date]
    expired_at: Optional[datetime.date]
    mu_intervals: list[float]
    dm_intervals: list[float]
    mu_holdings_time: list[float]
    dm_holdings_time: list[float]

    @validator('username')
    @classmethod
    def validate_username(cls, value):
        if not value.islower() or len(value.split()) != 1 or 4 > len(value):
            raise ValidationError('В имени пользователя используются строчные буквы без пробелов!')
        return value

    @validator('password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValidationError('Пароль должен быть длиной не менее 6 символов!')
        using_alphabet = set()
        for letter in value:
            for alphabet in alphabets:
                if letter in alphabet:
                    using_alphabet.update(alphabet)
                    break
            if len(using_alphabet) >= 30:
                return value
        raise ValidationError('Алфавит пароля должен быть мощностью не менее 30!')
