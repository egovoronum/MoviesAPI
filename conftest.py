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

load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

fake = Faker("ru_RU")

# session init 
@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()

# managing API
@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(
        session, 
        base_url=BASE_URL,
        auth_url=AUTH_URL
    )
    
# login API
@pytest.fixture(scope="session")
def api_login(session):
    return AuthAPI(session, AUTH_URL)
    
# test user
@pytest.fixture(scope="session")
def test_user():
    
    register_data = {
        "email": "lexluger@email.com",
        "fullName": "Lex Luger",
        "password": "12345678Aa",
        "passwordRepeat": "12345678Aa"
    }
    
    return register_data

#######LEGACY##########
    
# MAIN REQUESTER 
@pytest.fixture(scope="session")
def requester():
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)

# THIS REQUESTER IS FOR LOGIN AS ADMIN
@pytest.fixture(scope="session")
def login_requester():
    session = requests.Session()
    return CustomRequester(session=session, base_url=AUTH_URL)

# LOGIN AS ADMIN
@pytest.fixture(scope="session")
def login_admin(login_requester, requester):

    payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }

    response = login_requester.send_request(
        method = "POST",
        endpoint = LOGIN_ENDPOINT,
        data = payload,
        expected_status = 200
    )

    requester.session.headers.update({
        "Authorization": f"Bearer {response.json()['accessToken']}"
    })

    return response.json()

# CREATE MOVIE / yield RESPONSE
@pytest.fixture(scope="session")
def create_movie(requester, login_admin):

    payload = {
        "name": f"{fake.word()}",
        "imageUrl": "https://image.url",
        "price": 200,
        "description": "Описание фильма",
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    response = requester.send_request(
        method = "POST",
        endpoint = MOVIES_ENDPOINT,
        data = payload,
        expected_status=201
    )

    movie_id = response.json()["id"]

    yield response

    requester.send_request(
        method = "DELETE",
        endpoint = f"{MOVIES_ENDPOINT}/{movie_id}",
        expected_status = 200
    )

# CREATE INVALID MOVIE (negative PRICE, EMPTY: description, location, published, genreId / return response
@pytest.fixture(scope="session")
def create_invalid_movie(requester, login_admin):
    
    payload = {
        "name": f"{fake.word()}",
        "imageUrl": "https://image.url",
        "price": -200,
        "description": None,
        "location": None,
        "published": None,
        "genreId": None,
    }

    response = requester.send_request(
        method = "POST",
        endpoint = MOVIES_ENDPOINT,
        data = payload,
        expected_status = 400
    )

    return response


# DELETE MOVIE -> CREATE NEW and THEN DELETE
@pytest.fixture(scope="session")
def delete_movie(requester, login_admin):

    create_payload = {
        "name": f"{fake.word()}",
        "imageUrl": "https://image.url",
        "price": 200,
        "description": "Описание фильма",
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    create_response = requester.send_request(
        method = "POST",
        endpoint = MOVIES_ENDPOINT,
        data = create_payload,
        expected_status=201
    )

    movie_id = create_response.json()["id"]

    delete_response = requester.send_request(
        method = "DELETE",
        endpoint = f"{MOVIES_ENDPOINT}/{movie_id}",
        expected_status = 200
    )

    return delete_response

# PATCH MOVIE 2in1 positive -> CREATE NEW and THEN PATCH / returns tuple CREATE_RESPONSE & PATCH_RESPONSE [0] [1]
@pytest.fixture(scope="session")
def patch_movie(requester, login_admin):

    create_payload = {
        "name": f"{fake.word()}",
        "imageUrl": "https://image.url",
        "price": 200,
        "description": "Описание фильма",
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    create_response = requester.send_request(
        method = "POST",
        endpoint = MOVIES_ENDPOINT,
        data = create_payload,
        expected_status=201
    )

    movie_id = create_response.json()["id"]

    patch_payload = {
        "name": f"{create_response.json()['name']}_patched",
        "imageUrl": "https://image.url",
        "price": 200,
        "description": "Описание фильма",
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    patch_response = requester.send_request(
        method = "PATCH",
        endpoint = f"{MOVIES_ENDPOINT}/{movie_id}",
        data = patch_payload,
        expected_status = 200
    )

    yield create_response, patch_response

    requester.send_request(
        method = "DELETE",
        endpoint = f"{MOVIES_ENDPOINT}/{movie_id}",
        expected_status = 200
    )

# PATCH MOVIE negative -> CREATE NEW and THEN PATCH 
@pytest.fixture(scope="session")
def patch_invalid_movie(requester, login_admin):

    patch_payload = {
        "name": f"{fake.word()}",
        "imageUrl": "https://image.url",
        "price": 200,
        "description": "Описание фильма",
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    patch_response = requester.send_request(
        method = "PATCH",
        endpoint = f"{MOVIES_ENDPOINT}/{random.randint(1_000_001, 10_000_000)}",
        data = patch_payload,
        expected_status = 404
    )

    return patch_response

# !PATCH MOVIE negative -> WRONG FIELDS IN BODY
@pytest.fixture(scope="session")
def patch_movie_without_body(requester, login_admin):

    create_payload = {
        "name": f"{fake.word()}",
        "imageUrl": "https://image.url",
        "price": 200,
        "description": "Описание фильма",
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    create_response = requester.send_request(
        method = "POST",
        endpoint = MOVIES_ENDPOINT,
        data = create_payload,
        expected_status=201
    )

    movie_id = create_response.json()["id"]

    patch_payload = {
        "wassup": "wassup"
    }

    patch_response = requester.send_request(
        method = "PATCH",
        endpoint = f"{MOVIES_ENDPOINT}/{movie_id}",
        data = patch_payload,
        expected_status = 400
    )

    yield patch_response

    requester.send_request(
        method = "DELETE",
        endpoint = f"{MOVIES_ENDPOINT}/{movie_id}",
        expected_status = 200
    )

# FILTER FIXTURE (STRING QUERY!!) / pre-set params
@pytest.fixture(scope="session")
def filter_movies(requester):

    params = {
        "pageSize": 10,
        "page": 1,
        "minPrice": 1,
        "maxPrice": 1000,
        "locations": ["MSK", "SPB"],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    response = requester.send_request(
        method = "GET",
        endpoint = MOVIES_ENDPOINT,
        params = params,
        expected_status = 200
    )

    return response.json()

# FILTER COMBO TEST (STRING QUERY!!! NO BODY!)
@pytest.fixture(scope="session")
def filter_combo(requester):

    params = {
        "pageSize": 12,
        "page": 1,
        "minPrice": 1,
        "maxPrice": 1000,
        "locations": ["MSK"],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    response = requester.send_request(
        method = "GET",
        endpoint = MOVIES_ENDPOINT,
        params = params,
        expected_status = 200
    )

    return response.json()

# PRICE TEST (NO BODY, STRING QUERY!)
@pytest.fixture(scope="session")
def filter_movies_by_price(requester):

    params = {
        "pageSize": 10,
        "page": 1,
        "minPrice": 200,
        "maxPrice": 500,
        "locations": ["MSK", "SPB"],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    response = requester.send_request(
        method = "GET",
        endpoint = MOVIES_ENDPOINT,
        params = params,
        expected_status = 200
    )

    return response.json()

# INVALID PRICE TEST
@pytest.fixture(scope="session")
def filter_by_invalid_price(requester):

    params = {
        "pageSize": 10,
        "page": 1,
        "minPrice": 500,
        "maxPrice": 300,
        "locations": ["MSK", "SPB"],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    response = requester.send_request(
        method = "GET",
        endpoint = MOVIES_ENDPOINT,
        params = params,
        expected_status = 400
    )

    return response.json()

#INVALID PAGE TEST
@pytest.fixture(scope="session")
def filter_by_invalid_page(requester):

    params = {
        "pageSize": 10,
        "page": -1,
        "minPrice": 100,
        "maxPrice": 300,
        "locations": ["MSK", "SPB"],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    response = requester.send_request(
        method = "GET",
        endpoint = MOVIES_ENDPOINT,
        params = params,
        expected_status = 400
    )

    return response.json()
