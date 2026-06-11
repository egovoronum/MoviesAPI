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
from clients.movies_api import MoviesAPI

load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

fake = Faker("ru_RU")

#####################SETUP2#############################################################

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


#########################FIXTURES#######################################################


#* admin login data
@pytest.fixture(scope="session")
def admin_login():

    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }

    return login_data


# *get user by id
@pytest.fixture(scope="session")
def get_user():

    user_id = "734964ec-4d6a-4789-839f-75797141e73e"

    return user_id


# *test user + teardown after registration
@pytest.fixture(scope="session")
def test_user(session):
    
    api = ApiManager(session)

    admin_login = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }

    user = {
        "register_data": str("Empty"),
        "id": None
    }
    
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
        "passwordRepeat": password
    }
    
    user["register_data"] = register_data

    yield user

    if user["id"] is not None:

        response = api.auth_api.login_user(
            admin_login,
            expected_status=200
        )
        
        token = response.json()["accessToken"]
        
        session.headers.update({"Authorization": f"Bearer {token}"})

        api.user_api.delete_user(user["id"], expected_status=200)

############################MOVIES######################################################

# *gives a random movie ID from an int range
@pytest.fixture(scope="session")
def movie_id():

    id = random.randint(570, 580)

    return id


# *finds an existing movie and grabs ID
@pytest.fixture(scope="function")
def grab_movie(unauthenticated_api_manager, valid_filter_params):

    response = unauthenticated_api_manager.movies_api.get_movies(
        params=valid_filter_params,
        expected_status=200
    )

    data = response.json()

    movies = data["movies"]

    if len(movies) < 1:
        raise RuntimeError("Couldn't grab as movie list length is less than 1!")
    
    movie = movies[0]
    id = movie["id"]

    return id


# *prepares general valid filter parameters for /movies
@pytest.fixture(scope="session")
def valid_filter_params():

    params = {
        "pageSize": random.randint(1, 10),
        "page": 1,
        "minPrice": random.randint(1, 200),
        "maxPrice": random.randint(200, 1500),
        "locations": ["MSK", "SPB"],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    return params


# *prepares valid price filter parameters for /movies
@pytest.fixture(scope="session")
def valid_price_filter():

    params = {
        "pageSize": random.randint(1, 10),
        "page": 1,
        "minPrice": random.randint(1, 500),
        "maxPrice": random.randint(500, 2000),
        "locations": ["MSK", "SPB"],
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }

    return params


#* Prepares new movie data 
@pytest.fixture(scope="session")
def create_movie(admin_api_manager):

    data = {
        "name": f"{fake.word()} в {fake.word()}",
        "imageUrl": "https://example.com/image.png",
        "price": random.randint(50, 1000),
        "description": f"{fake.word()} вызвал сомнения у {fake.word()}",
        "location": "SPB",
        "published": True,
        "genreId": 1    
    }

    yield data

    #teardown
    admin_api_manager.movies_api.delete_movie(data["id"], expected_status=200)

#* Prepares patch data for editing a movie
@pytest.fixture(scope="session")
def patch_movie():

    data = {
        "name": f"{fake.word()} в {fake.word()}",
        "imageUrl": "https://example.com/image.png",
        "price": random.randint(50, 1000),
        "description": f"{fake.word()} вызвал сомнения у {fake.word()}",
        "location": "SPB",
        "published": True,
        "genreId": 1    
    }

    return data

###########################GENRES################################################

#* gets a list of random genres
@pytest.fixture(scope="session")
def get_genres(unauthenticated_api_manager):
    
    response = unauthenticated_api_manager.movies_api.get_genres(
        expected_status=200
    )
    data = response.json()

    return data

#* prepares an existing random genre ID 
@pytest.fixture(scope="function")
def random_genre(unauthenticated_api_manager):
    
    response = unauthenticated_api_manager.movies_api.get_genres(
        expected_status=200
    )

    genres = response.json()
    genre = random.choice(genres)
    genre_id = genre["id"]

    return genre_id

#* prepares random genre_data
@pytest.fixture(scope="function")
def genre_data(admin_api_manager):

    data = {
        "name": f"{fake.word()} усиленный {fake.word()}"
    }

    yield data

    genre_id = data["id"]

    try:
        admin_api_manager.movies_api.delete_genre(
            genre_id,
            expected_status=200
        )
    except Exception as e:
        f"Failed to delete genre with ID: {genre_id}"

