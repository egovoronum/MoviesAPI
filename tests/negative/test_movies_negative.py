from clients.api_manager import ApiManager

#! minPrice > maxPrice in filter
def test_invalid_price_filter(
        unauthenticated_api_manager: ApiManager,
        invalid_price_filter_reversed: dict
    ):

    response = unauthenticated_api_manager.movies_api.get_movies(
        invalid_price_filter_reversed, 
        expected_status=400
    )

    data = response.json()
    
    assert "minPrice must be less than maxPrice" in data["message"]


#! negative price in filter
def test_negative_price_filter(
        unauthenticated_api_manager: ApiManager, 
        invalid_price_filter_negative_min: dict
    ):

    response = unauthenticated_api_manager.movies_api.get_movies(
        invalid_price_filter_negative_min,
        expected_status=400
    )

    data = response.json()

    assert "Поле minPrice имеет минимальную величину 1" in data["message"]


#! negative page value in filter
def test_negative_page_filter(
        unauthenticated_api_manager: ApiManager,
        invalid_page: dict
    ):
    
    response = unauthenticated_api_manager.movies_api.get_movies(
        invalid_page,
        expected_status=400
    )

    data = response.json()

    assert "Поле page имеет минимальную величину 1" in data["message"], (
        f"No 'message' field in 'response.json()'"
    )


#! incorrect location value in filter
def test_invalid_location_filter(
        unauthenticated_api_manager: ApiManager,
        invalid_location: dict       
    ):

    response = unauthenticated_api_manager.movies_api.get_movies(
        invalid_location,
        expected_status=400
    )

    data = response.json()

    assert (
    "Каждое значение в поле locations должно быть одним из значений: MSK, SPB"
    in data["message"]
    ), (
    "No 'message' field in 'response.json()'"
    )


#! create invalid movie
def test_create_invalid_movie(
        admin_api_manager: ApiManager,
        invalid_movie_data: dict
    ):

    response = admin_api_manager.movies_api.create_movie(
        invalid_movie_data,
        expected_status=400
    )

    data = response.json()

    assert "Поле price должно быть больше 0" in data["message"]
    assert "Поле location должно быть одним из: MSK, SPB" in data["message"]
    assert "Bad Request" in data["error"]