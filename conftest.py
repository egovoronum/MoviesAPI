# ─── стандартные библиотеки ────────────────────────────────────────────
import os
import random

# ─── доп библиотеки ────────────────────────────────────────────────────────
import requests
import pytest, allure
from dotenv import load_dotenv
from faker import Faker
from sqlalchemy.orm import Session
from typing import Generator
from pytest_check import check
# ─── модули проекта ────────────────────────────────────────────────────────────
from utils.data_generator import DataGenerator
from clients.api_manager import ApiManager
from entities.user import User
from enums.roles import Roles
from models.base_models import Movie, Genre, CreateUserData, CreatedUser, TestUser, PatchResponseModel, PatchUserModel, CreateMovieData
from db_requester.db_helper import DBHelper
from db_requester.db_client import get_db_session

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
def oneshot_user() -> CreateUserData:
   
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

    model = CreateUserData.model_validate(register_data)

    return model


@pytest.fixture(scope="function")
def create_user_data(oneshot_user) -> CreateUserData:
    return oneshot_user.model_copy(update={"verified": True, "banned": False})


@pytest.fixture(scope="function")
def create_admin_user_data(oneshot_user) -> CreateUserData:

    return oneshot_user.model_copy(update={"roles": ["USER", "ADMIN"], "verified": True, "banned": False})
    

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


@pytest.fixture(scope="function")
def common_user(
    user_session,
    super_admin: User,
    create_user_data: CreateUserData
    ) -> Generator[User, None, None]:

    new_session = user_session()

    common_user = User(
        create_user_data.email,
        create_user_data.password,
        [Roles.USER],
        new_session)

    response = super_admin.api.user_api.create_user(create_user_data)

    data = response.json()
    new_common_user_id = data["id"]

    common_user.api.auth_api.authenticate(common_user.creds)

    yield common_user

    with allure.step("tearing down common_user"):
        super_admin.api.user_api.delete_user(
            new_common_user_id,
            expected_status=200
            )


@pytest.fixture(scope="function")
def admin_user(
    user_session,
    super_admin: User,
    create_admin_user_data: CreateUserData
) -> Generator[User, None, None]:
    
    new_session = user_session()

    admin_user = User(
        create_admin_user_data.email,
        create_admin_user_data.password,
        [Roles.ADMIN],
        new_session)

    with allure.step("Создаем юзера по модели CreateUserData"):
        response = super_admin.api.user_api.create_user(create_admin_user_data)
        data = response.json()

    with allure.step("сохраняем id для последующей передачи в teardown"):   
        new_admin_id = data["id"]

    with allure.step("""
        Фикстура немного заморочена, т.к. своеобразный API у movies
        создаем patch_data и делаем PATCH юзера
        т.к. невозможно указать ROLES: ["ADMIN"] при создании!
        """):   

        patch_data = {
            "roles": ["USER", "ADMIN"],
            "verified": True,
            "banned": False
            }

        patch_data_model = PatchUserModel.model_validate(patch_data)

        with allure.step("Патчим юзера, чтобы получить админа"):    
            patch_response = super_admin.api.user_api.patch_user(new_admin_id, patch_data_model)
            admin_user_model = PatchResponseModel.model_validate(patch_response.json())

        with allure.step("Убеждаемся что фикстура пропатчила и 'ADMIN' есть в roles"):
            with check:
                check.is_in("ADMIN", admin_user_model.roles, "у юзера нет роли ADMIN")
        
        with allure.step("логиним новоиспеченного админа"):    
            admin_user.api.auth_api.authenticate(admin_user.creds)

    yield admin_user

    with allure.step("teardown админа"):
        super_admin.api.user_api.delete_user(
            new_admin_id,
            expected_status=200
            )


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
def oneshot_genre(super_admin:User) -> Generator[Genre, None, None]:

    data = {
        "name": f"{fake.word()} и точка!!!"
    }

    response = super_admin.api.movies_api.create_genre(data, expected_status=201)

    genre_model = Genre.model_validate(response.json())
    genre_id = genre_model.id

    yield genre_model
    super_admin.api.movies_api.delete_genre(genre_id)


@pytest.fixture(scope="function")
def valid_movie_data(oneshot_genre: Genre) -> CreateMovieData:

    genre = oneshot_genre
    genre_id = genre.id

    data = {
        "name": f"{fake.word()} в {fake.word()}",
        "imageUrl": "https://example.com/image.png",
        "price": random.randint(50, 1000),
        "description": f"{fake.text(5)} вызвал сомнения у {fake.text(5)}",
        "location": "SPB",
        "published": True,
        "genreId": genre_id    
    }

    model = CreateMovieData.model_validate(data)

    return model


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
    

@pytest.fixture(scope="function")
def oneshot_movie(
    super_admin:User, 
    valid_movie_data:CreateMovieData
) -> Generator[Movie, None, None]:

    with allure.step("запрос на создание"):
        response = super_admin.api.movies_api.create_movie(
            valid_movie_data,
            expected_status=201)

    with allure.step("валидация модели"):
        movie_model =  Movie.model_validate(response.json())

        yield movie_model
    with allure.step("teardown"):
        super_admin.api.movies_api.delete_movie(movie_model.id, expected_status=200)


@pytest.fixture(scope="function")
def oneshot_movie_skip_teardown(
    super_admin:User, 
    valid_movie_data:CreateMovieData
    ) -> Movie:

    response = super_admin.api.movies_api.create_movie(
        valid_movie_data,
        expected_status=201)
    movie_model =  Movie.model_validate(response.json())

    return movie_model

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:

    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:

    db_helper = DBHelper(db_session)
    return db_helper

@pytest.fixture(scope="function")
def created_test_dbuser(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_db_user_data())
    yield user
    # Cleanup после теста
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)

@pytest.fixture(scope="function")
def db_movie_data(db_helper):
    """
    Фикстура, которая создает фильм в БД
    и удаляет его после завершения теста
    """
    movie = db_helper.create_test_movie(DataGenerator.generate_db_movie_data())
    yield movie

    if db_helper.get_movie_by_id(movie.id):
        db_helper.delete_movie(movie)


@pytest.fixture(scope="session")
def get_user():

    user_id = "734964ec-4d6a-4789-839f-75797141e73e"

    return user_id


@pytest.fixture(scope="function")
def invalid_movie_id():

    id = random.randint(500000, 600000)

    return id