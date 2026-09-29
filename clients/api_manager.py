from clients.auth_api import AuthAPI
from clients.user_api import UserAPI
from clients.movies_api import MoviesAPI
import requests
import allure

class ApiManager:
    def __init__(self, session: requests.Session):
            self.session = session
            self.auth_api = AuthAPI(session)
            self.user_api = UserAPI(session)
            self.movies_api = MoviesAPI(session)

    allure.step("ApiManager - закрыть сессию")
    def close_session(self):
        self.session.close()

             
