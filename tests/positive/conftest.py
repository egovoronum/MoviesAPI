import requests, pytest, random
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

#? обычный юзер 
@pytest.fixture(scope="session")
def user_api_manager(registered_user):

    http_session = requests.Session()
    user_api_manager = ApiManager(http_session)
    user_api_manager.auth_api.authenticate(registered_user)
    
    yield user_api_manager

    http_session.close()


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

#* prepare user and return registration payload for SESSION
@pytest.fixture(scope="session")
def prepared_user():
    
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

    return register_data

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
        "passwordRepeat": password
    }

    return register_data  

#* register user
@pytest.fixture(scope="session")
def registered_user(
    unauthenticated_api_manager: ApiManager,
    admin_api_manager: ApiManager,
    prepared_user: dict
    ):

    response = unauthenticated_api_manager.auth_api.register_user(
        user_data=prepared_user,
        expected_status=201
    )

    created_user = response.json()
    id = created_user["id"]

    data = [prepared_user["email"], prepared_user["password"]]

    yield data

    admin_api_manager.auth_api.delete_user(
            id,
            expected_status=200
        )


# *creates a test user + teardown
@pytest.fixture(scope="function")
def test_user(admin_api_manager: ApiManager):

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
    
    yield register_data

    user_id = register_data["id"]

    admin_api_manager.auth_api.delete_user(
            user_id,
            expected_status=200
        )

# user deletion
@pytest.fixture(scope="function")
def test_user_deletion(unauthenticated_api_manager: ApiManager,
                       oneshot_user: dict
                       ):

    response = unauthenticated_api_manager.auth_api.register_user(
            user_data=oneshot_user,
            expected_status=201
        )

    oneshot_user = response.json()
    id = oneshot_user["id"]

    return id

    
#* PREPARES NEW MOVIE DATA
@pytest.fixture(scope="function")
def new_movie_data(unauthenticated_api_manager):

    #grab existing random genre first to avoid error
    response = unauthenticated_api_manager.movies_api.get_genres(
        expected_status=200
    )

    genres = response.json()
    genre = random.choice(genres)
    genre_id = genre["id"]

    data = {
        "name": f"{fake.word()} в {fake.word()}",
        "imageUrl": "https://example.com/image.png",
        "price": random.randint(50, 1000),
        "description": f"{fake.text(10)} не все так однозначно с {fake.text(10)}",
        "location": "SPB",
        "published": True,
        "genreId": genre_id  
    }

    return data

#* CREATES NEW MOVIE & tears it down
@pytest.fixture(scope="function")
def create_test_movie(
    admin_api_manager: ApiManager,
    new_movie_data: dict):

    response = admin_api_manager.movies_api.create_movie(
        new_movie_data,
        expected_status=201
    )

    data = response.json()

    yield data

    #teardown
    admin_api_manager.movies_api.delete_movie(data["id"], expected_status=200)


# *grabs movie ID from create_test_movie
@pytest.fixture(scope="function")
def movie_id(create_test_movie):

    id = create_test_movie["id"]

    return id

#* grabs invalid movie ID
@pytest.fixture(scope="function")
def invalid_movie_id():

    id = random.randint(500000, 600000)

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
    
    movie = movies[1]
    id = movie["id"]

    return id

@pytest.fixture(scope="session")
def filter_parameters():

    parameters = {
        "pageSize": 10,
        "page": 1,
        "minPrice": 500,
        "maxPrice": 1000,
        "locations": ["MSK", "SPB"],
        "published": True,
    }

    return parameters

# *prepares general valid filter parameters for /movies
@pytest.fixture(scope="function")
def valid_filter_params():

    params = {
        "pageSize": 10,
        "page": 1,
        "minPrice": 1,
        "maxPrice": 1000,
        "locations": "MSK",
        "published": True,
        "createdAt": "asc"
    }

    return params


# *prepares valid price filter parameters for /movies
@pytest.fixture(scope="function")
def valid_price_filter():

    params = {
        "pageSize": random.randint(1, 10),
        "page": 1,
        "minPrice": random.randint(1, 500),
        "maxPrice": random.randint(500, 2000),
        "locations": ["MSK", "SPB"],
        "published": True,
        "createdAt": "asc"
    }

    return params


#* Prepares ascending filter for movies
@pytest.fixture(scope="function")
def asc_filter():

    params = {
        "pageSize": random.randint(5, 10),
        "page": 1,
        "minPrice": random.randint(1, 100),
        "maxPrice": random.randint(100, 2000),
        "locations": ["MSK", "SPB"],
        "published": True,
        "createdAt": "asc"
    }

    return params


#* Prepares descending filter for movies
@pytest.fixture(scope="function")
def desc_filter():

    params = {
        "pageSize": random.randint(5, 10),
        "page": 1,
        "minPrice": random.randint(1, 100),
        "maxPrice": random.randint(100, 2000),
        "locations": ["MSK", "SPB"],
        "published": True,
        "createdAt": "desc"
    }

    return params


#* Prepares patch data for editing a movie
@pytest.fixture(scope="function")
def patch_movie():

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
        f"Failed to delete genre with ID at teardown: {genre_id}"


#* Parses GET movies list until it finds a movie with a review
@pytest.fixture(scope="function")
def grab_movie_with_reviews(
    unauthenticated_api_manager: ApiManager,
    valid_filter_params: dict
    ):

    response_movie_id = unauthenticated_api_manager.movies_api.get_movies(
        params=valid_filter_params,
        expected_status=200
    )

    data = response_movie_id.json()

    movies = data["movies"]
    movie_with_reviews = None

    if len(movies) < 1:
        raise RuntimeError("Couldn't grab as movie list length is less than 1!")
    
    movie = movies[0]

    for movie in movies:    

        movie_id = movie["id"]

        response_review = unauthenticated_api_manager.movies_api.get_review(
            movie_id,
            expected_status=200
        )

        reviews = response_review.json()

        if len(reviews) > 0:
            movie_with_reviews = movie_id
            break
    
    if movie_with_reviews is None:
        pytest.skip("No movies with reviews found")

    return movie_with_reviews

#* POSTS a review to an existing movie
@pytest.fixture(scope="function")
def generate_review(admin_api_manager):
    
    data = {
    "rating": 5,
    "text": f"Отличный фильм, вызывает {fake.word()}"
    }

    yield data

    params = {}

    params["movieId"] = data["movieId"]
    params["userId"] = data["userId"]

    try:
        admin_api_manager.movies_api.delete_review(
            params=params,
            expected_status=200
        )

    except Exception as e:
        f"Failed to delete review with ID at teardown: {params["userId"]}"
