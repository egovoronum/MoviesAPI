# use this to generate user data like emails, names and etc. 
import random
import string
from datetime import datetime

from faker import Faker
faker = Faker()

class DataGenerator:
    
    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    def generate_random_name():
        return f"{faker.first_name()} {faker.last_name()}"
         
    @staticmethod
    def generate_random_password():
        """
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        """
        # Гарантируем наличие хотя бы одной буквы и одной цифры
        letters = random.choice(string.ascii_letters)  # Одна буква
        digits = random.choice(string.digits)  # Одна цифра

        # Дополняем пароль случайными символами из допустимого набора
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)  # Остальная длина пароля
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        # Перемешиваем пароль для рандомизации
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    def generate_invalid_password():
        letters = string.punctuation + string.ascii_letters
        return ''.join(random.choices(letters, k=5))

    @staticmethod
    def generate_db_user_data() -> dict:
        """Генерирует данные для тестового пользователя"""
        from uuid import uuid4

        return {
            'id': f'{uuid4()}',  # генерируем UUID как строку
            'email': DataGenerator.generate_random_email(),
            'full_name': DataGenerator.generate_random_name(),
            'password': DataGenerator.generate_random_password(),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'verified': False,
            'banned': False,
            'roles': '{USER}'
        }

    @staticmethod
    def generate_db_movie_data() -> dict:

        return {
            'id': random.randint(1, 10000),
            'name': f"{faker.unique.word()} Kimbo Slice",
            'price': random.randint(1, 100),
            'description': f"{faker.word()} generated db data for {faker.word()}",
            'image_url': f"{faker.image_url()}",
            'location': "MSK",
            'published': True,
            'rating': faker.pyfloat(min_value=1, max_value=5, right_digits=1),
            'genre_id': 9,
            'created_at': datetime.now()
            }