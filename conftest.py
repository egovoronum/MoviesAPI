import requests, pytest
from constants import admin_creds, BASE_URL, HEADERS, LOGIN_ENDPOINT, LOGOUT_ENDPOINT, REGISTER_ENDPOINT, MOVIES_ENDPOINT
from utils.data_generator import DataGenerator
from faker import Faker
from custom_requester.custom_requester import CustomRequester

faker = Faker()

@pytest.fixture(scope="session")
def requester():
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)

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
        expected_status = 200,
    )

    return response.json()

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
        expected_status = 200,
    )

    return response.json()

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