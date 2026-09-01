import requests, pytest, random
from constants import (
    BASE_URL, HEADERS, LOGIN_ENDPOINT, LOGOUT_ENDPOINT, 
    REGISTER_ENDPOINT, MOVIES_ENDPOINT, AUTH_URL
)
from utils.data_generator import DataGenerator
from faker import Faker
from custom_requester.custom_requester import CustomRequester
from dotenv import load_dotenv
import os

from clients.api_manager import ApiManager
from clients.auth_api import AuthAPI
from clients.user_api import UserAPI

load_dotenv()

def env_check(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Required environment variable '{name}' is missing")
    return value

ADMIN_EMAIL = env_check("ADMIN_EMAIL")
ADMIN_PASSWORD = env_check("ADMIN_PASSWORD")

fake = Faker("ru_RU")


# session init 
@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()


# Admin API manager
@pytest.fixture(scope="session")
def admin_api_manager():
    
    http_session = requests.Session()
    admin_api_manager = ApiManager(http_session)
    admin_api_manager.auth_api.authenticate([ADMIN_EMAIL, ADMIN_PASSWORD])
    
    yield admin_api_manager
    
    http_session.close()

#? нигде не юзаю... managing API 
@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)


@pytest.fixture(scope="session")
def unauthenticated_api_manager():

    http_session = requests.Session()

    yield ApiManager(http_session)

    http_session.close()
    

# login API
@pytest.fixture(scope="session")
def api_login(session):

    return AuthAPI(session)


# !prepares an invalid price filter minPrice>maxPrice
@pytest.fixture(scope="session")
def invalid_price_filter_reversed():
    
    params = {
        "pageSize": random.randint(1, 10),
        "page": 1,
        "minPrice": 1000,
        "maxPrice": 100,
        "locations": ["MSK", "SPB"],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    return params

# !prepares an invalid price filter minPrice is negative
@pytest.fixture(scope="session")
def invalid_price_filter_negative_min():
    
    params = {
        "pageSize": random.randint(1, 10),
        "page": 1,
        "minPrice": -50,
        "maxPrice": 500,
        "locations": ["MSK", "SPB"],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    return params

#! prepares an invalid page value in filter
@pytest.fixture(scope="session")
def invalid_page():

    params = {
        "pageSize": random.randint(1, 10),
        "page": -1,
        "minPrice": 100,
        "maxPrice": 1000,
        "locations": ["MSK", "SPB"],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    return params

#! prepares an invalid location field in filter
@pytest.fixture(scope="session")
def invalid_location():

    params = {
        "pageSize": random.randint(10, 20),
        "page": 1,
        "minPrice": 1,
        "maxPrice": 10000,
        "locations": ["TOKYO"],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    return params
    

#! Prepares invalid movie data 
@pytest.fixture(scope="session")
def invalid_movie_data(admin_api_manager):

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
    