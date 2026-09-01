import requests, pytest, random
from utils.data_generator import DataGenerator
from faker import Faker
fake = Faker("ru_RU")
from custom_requester.custom_requester import CustomRequester

from dotenv import load_dotenv
load_dotenv()

import os

from clients.api_manager import ApiManager
from clients.auth_api import AuthAPI
from clients.user_api import UserAPI
from clients.movies_api import MoviesAPI
from entities.user import User

def env_check(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Required environment variable '{name}' is missing")
    return value

ADMIN_EMAIL = env_check("ADMIN_EMAIL")
ADMIN_PASSWORD = env_check("ADMIN_PASSWORD")

#* prepare oneshot user
@pytest.fixture(scope="function")
def oneshot_user():
   
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
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        ADMIN_EMAIL,
        ADMIN_PASSWORD,
        ["SUPER_ADMIN"],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture(scope="function")
def create_user_data(oneshot_user):
    updated_data = oneshot_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data


