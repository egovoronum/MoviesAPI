# ─── стандартные библиотеки ────────────────────────────────────────────
import os
import random

# ─── доп библиотеки ────────────────────────────────────────────────────────
import requests
import pytest
from dotenv import load_dotenv
from faker import Faker

# ─── модули проекта ────────────────────────────────────────────────────────────
from utils.data_generator import DataGenerator
from custom_requester.custom_requester import CustomRequester
from clients.api_manager import ApiManager
from clients.auth_api import AuthAPI
from clients.user_api import UserAPI
from clients.movies_api import MoviesAPI
from entities.user import User
from enums.roles import Roles

# ─── init─────────────────────────────────────────────────────────────
fake = Faker("ru_RU")
load_dotenv()


def env_check(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Required environment variable '{name}' is missing")
    return value

ADMIN_EMAIL = env_check("ADMIN_EMAIL")
ADMIN_PASSWORD = env_check("ADMIN_PASSWORD")


@pytest.fixture(scope="function")
def oneshot_user() -> dict[str, str]:
   
    password = fake.password(
        length=12,
        special_chars=False,
        digits=True,
        upper_case=True,
        lower_case=True
    )

    register_data = {
        "email": DataGenerator.generate_random_email(),
        "fullName": fake.name(),
        "password": password,
        "passwordRepeat": password,
    }

    return register_data  


@pytest.fixture(scope="function")
def create_user_data(oneshot_user) -> dict:
    updated_data = oneshot_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data


@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def common_user(user_session, super_admin: User, create_user_data: dict) -> User:
    new_session = user_session()

    common_user = User(
        create_user_data['email'],
        create_user_data['password'],
        [Roles.USER],
        new_session)

    super_admin.api.user_api.create_user(create_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)

    return common_user


@pytest.fixture
def admin_user(user_session, super_admin: User, create_user_data: dict) -> User:
    new_session = user_session()

    admin_user = User(
        create_user_data['email'],
        create_user_data['password'],
        [Roles.ADMIN],
        new_session)

    super_admin.api.user_api.create_user(create_user_data)
    admin_user.api.auth_api.authenticate(admin_user.creds)

    return admin_user


@pytest.fixture
def super_admin(user_session) -> User:
    new_session = user_session()

    super_admin = User(
        ADMIN_EMAIL,
        ADMIN_PASSWORD,
        [Roles.SUPER_ADMIN],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)

    return super_admin


@pytest.fixture(scope="function")
def valid_movie_data() -> dict:

    data = {
        "name": f"{fake.word()} в {fake.word()}",
        "imageUrl": "https://example.com/image.png",
        "price": random.randint(50, 1000),
        "description": f"{fake.text(5)} вызвал сомнения у {fake.text(5)}",
        "location": "SPB",
        "published": True,
        "genreId": 1    
    }

    return data    


@pytest.fixture(scope="session")
def invalid_movie_data() -> dict:

    data = {
        "name": f"{fake.word()} в {fake.word()}",
        "imageUrl": "https://example.com/image.png",
        "price": random.randint(-50, -1),
        "description": f"{fake.word()} вызвал сомнения у {fake.word()}",
        "location": "TOKYO",
        "published": False,
        "genreId": 1
    }

    return data 
    


