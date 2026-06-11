from clients.api_manager import ApiManager

def test_get_movie(api_manager: ApiManager, movie_id:int):

    response = api_manager.movies_api.get_movie(movie_id)
    data = response.json()

    assert data["id"] == movie_id



