from clients.api_manager import ApiManager

#* test GET random movie ID // ACCEPTS 200 & 404
def test_get_movie(unauthenticated_api_manager:ApiManager, movie_id:int):

    response = unauthenticated_api_manager.movies_api.get_movie(
        movie_id, 
        expected_status=[200, 404]
    )

    data = response.json()

    if response.status_code == 200:
        assert data["id"] == movie_id
    
    if response.status_code == 404:
        assert "Фильм не найден" in data["message"]
        assert "Not Found" in data["error"]


#* test if fields are correct in /MOVIES list
def test_get_movies(
        unauthenticated_api_manager:ApiManager,
        valid_filter_params:dict
    ):
    
    params = valid_filter_params
    page_size = params["pageSize"]
    
    response = unauthenticated_api_manager.movies_api.get_movies(
        valid_filter_params, 
        expected_status=200
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


#* test if price filter works
def test_get_movies_by_price(
        unauthenticated_api_manager:ApiManager,
        valid_price_filter:dict
    ):

    params = valid_price_filter
    min_price = params["minPrice"]
    max_price = params["maxPrice"]

    response = unauthenticated_api_manager.movies_api.get_movies(
        params, 
        expected_status=200
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


#* test create and teardown a movie
def test_create_movie(admin_api_manager: ApiManager, create_movie:dict):
    
    movie_data = create_movie

    response = admin_api_manager.movies_api.create_movie(
        movie_data,
        expected_status=201
    )

    data = response.json()

    assert create_movie["name"] == data["name"], (
        f"Names don't match!"
    )

    #teardown
    create_movie["id"] = data["id"]


#* test delete random movie from DB
def test_delete_movie(admin_api_manager: ApiManager, grab_movie:int):

    movie_id = grab_movie

    response = admin_api_manager.movies_api.delete_movie(
        movie_id,
        expected_status=200
    )

    data = response.json()

    assert movie_id == data["id"]