from custom_requester.custom_requester import CustomRequester

class MoviesAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session, base_url="https://api.dev-cinescope.coconutqa.ru")
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
            endpoint=f"/movies/",
            params=params,
            expected_status=expected_status
        )