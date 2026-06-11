from clients.api_manager import ApiManager

#* Get a random movie & check ID mismatch
def test_get_movie(unauthenticated_api_manager:ApiManager, movie_id:int):

    response = unauthenticated_api_manager.movies_api.get_movie(
        movie_id, expected_status=200
    )
    data = response.json()

    assert data["id"] == movie_id

#* Unauthenticated GET MOVIES list. Check if response has all fields..
def test_get_movies(unauthenticated_api_manager:ApiManager, valid_filter_params:dict):
    
    params = valid_filter_params
    page_size = params["pageSize"]
    
    response = unauthenticated_api_manager.movies_api.get_movies(
        valid_filter_params, expected_status=200
    )
    
    data = response.json()
    movies = data["movies"]
    
    assert len(movies) > 0, f"Returned empty list"
    assert page_size == data["pageSize"], f"pageSize mismatch"
    assert "id" in movies[0], (
        f"No ID in movies[0], did you get the correct list in response?"
    )
    assert "id" in movies[0], "No ID in movies[0]"
    assert "genreId" in movies[0], "No genreId in movies[0]"        
    assert "imageUrl" in movies[0], "No imageUrl in movies[0]"        
    assert "price" in movies[0], "No price in movies[0]"
    assert "rating" in movies[0], "No rating in movies[0]"
    assert "location" in movies[0], "No location in movies[0]"
    assert "published" in movies[0], "No published in movies[0]"
    assert "createdAt" in movies[0], "No createdAt in movies[0]"
    assert "genre" in movies[0], "No genre object in movies[0]"
    assert "name" in movies[0]["genre"], "No genre.name in movies[0]"

#* Unauthenticated GET MOVIES list. Test if price filter works.
def test_get_movies_by_price(unauthenticated_api_manager:ApiManager, valid_price_filter):

    params = valid_price_filter
    min_price = params["minPrice"]
    max_price = params["maxPrice"]

    response = unauthenticated_api_manager.movies_api.get_movies(
        params, expected_status=200
    )
    
    data = response.json()
    movies = data["movies"]

    for movie in movies:
        assert movie["price"] >= min_price, (
            f"Price out of specified range. Look at min_price"
        )
        assert movie["price"] <= max_price, (
            f"Price out of specified range. Look at max_price"
        )