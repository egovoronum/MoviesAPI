from custom_requester.custom_requester import CustomRequester
import requests
import allure
from constants import BASE_URL

class MoviesAPI(CustomRequester):
    def __init__(self, session: requests.Session):
        super().__init__(session, base_url=BASE_URL)
        self.session=session

    @allure.step("Получить фильм по ID")
    def get_movie(self, movie_id:int, expected_status=[200, 404]):
        return self.send_request(
            method="GET",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status
        )

    @allure.step("Получить список фильмов с параметрами")
    def get_movies(self, params:dict, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/movies",
            params=params,
            expected_status=expected_status
        )

    @allure.step("Создать новый фильм")
    def create_movie(self, movie_data:dict, expected_status=200):
        return self.send_request(
            method="POST",
            endpoint=f"/movies",
            data=movie_data,
            expected_status=expected_status
        )

    @allure.step("Удалить фильм по ID")    
    def delete_movie(self, movie_id:int, expected_status=200):
        return self.send_request(
            method="DELETE",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status
        )

    @allure.step("Обновить фильм по ID (patch)")
    def patch_movie(self, data:dict, movie_id:int, expected_status=200):
        return self.send_request(
            method="PATCH",
            data=data,
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status
        )

    @allure.step("Получить жанр по ID")
    def get_genre(self, genre_id:int, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/genres/{genre_id}",
            expected_status=expected_status
        )

    @allure.step("Получить список жанров")
    def get_genres(self, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/genres",
            expected_status=expected_status
        )

    @allure.step("Создать новый жанр")
    def create_genre(self, data:dict, expected_status=200):
        return self.send_request(
            method="POST",
            data=data,
            endpoint=f"/genres",
            expected_status=expected_status
        )

    @allure.step("Удалить жанр по ID")
    def delete_genre(self, genre_id, expected_status=200):
        return self.send_request(
            method="DELETE",
            endpoint=f"/genres/{genre_id}",
            expected_status=expected_status
        )

    @allure.step("Получить отзывы к фильму")
    def get_review(self, movie_id, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/movies/{movie_id}/reviews",
            expected_status=expected_status
        )

    @allure.step("Добавить отзыв к фильму")
    def post_review(self, movie_id:int, data:dict, expected_status=201):
        return self.send_request(
            method="POST",
            data = data,
            endpoint=f"/movies/{movie_id}/reviews",
            expected_status=expected_status
        )

    @allure.step("Удалить отзыв к фильму")
    def delete_review(self, movie_id:int, params:dict, expected_status=200):
        return self.send_request(
            method="DELETE",
            params=params,
            endpoint=f"/movies/{movie_id}/reviews",
            expected_status=expected_status
        )
    