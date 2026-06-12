from clients.api_manager import ApiManager
from utils.time_util import iso_now

#* test GET movie / expect 404
def test_get_404movie(
        unauthenticated_api_manager: ApiManager,
        movie_id: int
    ):

    response = unauthenticated_api_manager.movies_api.get_movie(
        movie_id, 
        expected_status=404
    )

    data = response.json()

    assert "Фильм не найден" in data["message"]
    assert "Not Found" in data["error"]


#* test GET movie validity / expect 200
def test_get_200movie(
        unauthenticated_api_manager: ApiManager,
        grab_movie: int
    ):

    response = unauthenticated_api_manager.movies_api.get_movie(
        grab_movie,
        expected_status=200
    )

    data = response.json()

    assert "id" in data
    assert "name" in data
    assert "price" in data
    assert "description" in data
    assert "imageUrl" in data
    assert "location" in data
    assert "published" in data
    assert "rating" in data
    assert "genreId" in data
    assert "createdAt" in data
    assert "reviews" in data
    assert "genre" in data

#* test GET movieS list validity / expect 200
def test_get_movies(
        unauthenticated_api_manager: ApiManager,
        valid_filter_params: dict
    ):
    
    page_size = valid_filter_params["pageSize"]
    
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
        unauthenticated_api_manager: ApiManager,
        valid_price_filter: dict
    ):

    params = valid_price_filter
    min_price = params["minPrice"]
    max_price = params["maxPrice"]

    response = unauthenticated_api_manager.movies_api.get_movies(
        params=params, 
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


#* test filter ASC
def test_get_movies_asc(
        unauthenticated_api_manager: ApiManager,
        asc_filter: dict
    ):
    
    response = unauthenticated_api_manager.movies_api.get_movies(
        params=asc_filter,
        expected_status=200
    )

    data = response.json()
    movies = data["movies"]
    
    previous = "1900-05-26T11:00:15.900Z"
    
    for movie in movies:
        
        assert "createdAt" in movie, (f"No createdAt in movie.")
        current = movie["createdAt"]
        assert current >= previous, f"createdAt sorting broken: {current} < {previous}"
        previous = current


#* test filter DESC
def test_get_movies_desc(
        unauthenticated_api_manager: ApiManager,
        desc_filter: dict
    ):
    
    response = unauthenticated_api_manager.movies_api.get_movies(
        params=desc_filter,
        expected_status=200
    )

    data = response.json()
    movies = data["movies"]
    
    previous = "2500-05-26T11:00:15.900Z"
    
    for movie in movies:
        
        assert "createdAt" in movie, (f"No createdAt in movie.")
        current = movie["createdAt"]
        assert current < iso_now(), f"CreatedAt is > than current time. Double-check."
        assert current <= previous, f"createdAt sorting broken: {current} > {previous}"
        previous = current
        

#* test create and teardown a movie
def test_create_movie(
        admin_api_manager: ApiManager,
        create_movie: dict
    ):
    
    response = admin_api_manager.movies_api.create_movie(
        create_movie,
        expected_status=201
    )

    data = response.json()

    assert create_movie["name"] == data["name"], (
        f"Names don't match!"
    )

    #teardown
    create_movie["id"] = data["id"]


#* test delete random movie from DB
def test_delete_movie(
        admin_api_manager: ApiManager,
        grab_movie: int
    ):

    response = admin_api_manager.movies_api.delete_movie(
        grab_movie,
        expected_status=200
    )

    data = response.json()

    assert grab_movie == data["id"]


#* test patching random movie from DB
def test_patch_random_movie(
        admin_api_manager: ApiManager,
        grab_movie: int, 
        patch_movie: dict
    ):

    response = admin_api_manager.movies_api.patch_movie(
        patch_movie,
        grab_movie,
        expected_status=200
    )

    data = response.json()

    assert "name" in data, f"No name field in response."
    assert data["name"] == patch_movie["name"], (
        f"Name hasn't been patched."
    )
    assert "price" in data, f"No price field in response."
    assert data["price"] == patch_movie["price"], (
        f"Price hasn't been patched."
    )    

##############################GENRES####################################################

#* test if genres list has necessary fields
def test_get_genres(
        get_genres: dict
    ):

    genres = get_genres

    for genre in genres:
        assert "id" in genre
        assert "name" in genre


#* test get random genre
def test_get_random_genre(
        unauthenticated_api_manager: ApiManager,
        random_genre: int,
    ):

    response = unauthenticated_api_manager.movies_api.get_genre(
        random_genre,
        expected_status=200
    )

    data = response.json()

    assert "id" in data, f"No ID in data"
    assert "name" in data, f"No name in data"


#* test genre creation
def test_create_random_genre(
        admin_api_manager:ApiManager,
        genre_data:dict
    ):

    response = admin_api_manager.movies_api.create_genre(
        genre_data,
        expected_status=201
    )

    data = response.json()
    
    assert "id" in data
    assert "name" in data

    genre_data["id"] = data["id"]


#* test genre deletion
def test_delete_random_genre(
        admin_api_manager: ApiManager,
        random_genre: int
    ):

    genre_id = random_genre

    response = admin_api_manager.movies_api.delete_genre(
        genre_id,
        expected_status=200
    )

    data = response.json()

    assert "id" in data, f"No ID in data"
    assert "name" in data, f"No name in data"

###########################REVIEWS######################################################