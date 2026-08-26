from custom_requester.custom_requester import CustomRequester
import requests
from constants import BASE_URL

class MoviesAPI(CustomRequester):
    def __init__(self, session: requests.Session):
        super().__init__(session, base_url=BASE_URL)
        self.session=session

    def get_movie(self, movie_id:int, expected_status=[200, 404]):
        return self.send_request(
            method="GET",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status
        )
    
    def get_movies(self, params:dict, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/movies",
            params=params,
            expected_status=expected_status
        )
    
    def create_movie(self, movie_data:dict, expected_status=200):
        return self.send_request(
            method="POST",
            endpoint=f"/movies",
            data=movie_data,
            expected_status=expected_status
        )
    
    def delete_movie(self, movie_id:int, expected_status=200):
        return self.send_request(
            method="DELETE",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status
        )
    
    def patch_movie(self, data:dict, movie_id:int, expected_status=200):
        return self.send_request(
            method="PATCH",
            data=data,
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status
        )

    def get_genre(self, genre_id:int, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/genres/{genre_id}",
            expected_status=expected_status
        )
    
    def get_genres(self, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/genres",
            expected_status=expected_status
        )
    
    def create_genre(self, data:dict, expected_status=200):
        return self.send_request(
            method="POST",
            data=data,
            endpoint=f"/genres",
            expected_status=expected_status
        )

    def delete_genre(self, genre_id, expected_status=200):
        return self.send_request(
            method="DELETE",
            endpoint=f"/genres/{genre_id}",
            expected_status=expected_status
        )
    
    def get_review(self, movie_id, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/movies/{movie_id}/reviews",
            expected_status=expected_status
        )
    
    def post_review(self, movie_id:int, data:dict, expected_status=201):
        return self.send_request(
            method="POST",
            data = data,
            endpoint=f"/movies/{movie_id}/reviews",
            expected_status=expected_status
        )
    
    def delete_review(self, movie_id:int, params:dict, expected_status=200):
        return self.send_request(
            method="DELETE",
            params=params,
            endpoint=f"/movies/{movie_id}/reviews",
            expected_status=expected_status
        )
    