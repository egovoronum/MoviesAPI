##############################SETUP#####################################################

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

# *API classes import

from clients.api_manager import ApiManager
from clients.auth_api import AuthAPI
from clients.user_api import UserAPI

load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

fake = Faker("ru_RU")

################################SETUP2###################################################

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


# managing API for unauthenticated sessions
@pytest.fixture(scope="session")
def unauthenticated_api_manager():

    http_session = requests.Session()

    yield ApiManager(http_session)

    http_session.close()
    

# login API
@pytest.fixture(scope="session")
def api_login(session):

    return AuthAPI(session)

    
#############################FIXTURES###################################################

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
        "pageSize": random.randint(1, 10),
        "page": 1,
        "minPrice": 100,
        "maxPrice": 1000,
        "locations": ["TOKYO", 32],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    return params
    
###############################END######################################################