import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT, LOGOUT_ENDPOINT
import pytest
from utils.data_generator import DataGenerator

@pytest.fixture(scope="session")
def session_user():
    
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()
    session_user = {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER", "ADMIN"]
    }
    return session_user

@pytest.fixture(scope="session")
def patched_session_user(session_user):
    patched_session_user = session_user
    patched_session_user["roles"] == ["USER"]
    return patched_session_user

@pytest.fixture(scope="session")
def auth_session(session_user):
    login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
    login_data = {
        "email": session_user["email"],
        "password": session_user["password"]
    }
    response = requests.post(login_url, json=login_data, headers=HEADERS)
    assert response.status_code == 200, "Ошибка авторизации"
    token = response.json().get("accessToken")
    assert token is not None, "Токен доступа отсутствует в ответе"
    session = requests.Session()
    session.headers.update(HEADERS)
    session.headers.update({"Authorization": f"Bearer {token}"})
    return session

@pytest.fixture(scope="session")
def get_user_id(session_user):
    url = f"{BASE_URL}/{session_user["email"]}"
    response = requests.get(url)
    user_data = response.json()
    return user_data["id"]

@pytest.fixture(scope="session")
def logout(auth_session):
    logout_url = f"{BASE_URL}{LOGOUT_ENDPOINT}"
    response = requests.get(logout_url, headers=auth_session.headers)
    status_code = response.status_code
    assert status_code == 200, f"Expected 200, got: {status_code}"
    return response

