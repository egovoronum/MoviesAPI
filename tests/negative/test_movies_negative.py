from clients.api_manager import ApiManager

#! minPrice > maxPrice in filter
def test_invalid_price_filter(
        unauthenticated_api_manager:ApiManager,
        invalid_price_filter_reversed
    ):

    params = invalid_price_filter_reversed

    response = unauthenticated_api_manager.movies_api.get_movies(
        params, 
        expected_status=400
    )

    data = response.json()
    
    assert "minPrice must be less than maxPrice" in data["message"]

#! negative price in filter
def test_negative_price_filter(
        unauthenticated_api_manager:ApiManager, 
        invalid_price_filter_negative_min
    ):

    params = invalid_price_filter_negative_min

    response = unauthenticated_api_manager.movies_api.get_movies(
        params,
        expected_status=400
    )

    data = response.json()

    assert "Поле minPrice имеет минимальную величину 0" in data["message"]

#! negative page value in filter
def test_negative_page_filter(
        unauthenticated_api_manager:ApiManager,
        invalid_page
    ):
    
    params = invalid_page

    response = unauthenticated_api_manager.movies_api.get_movies(
        params,
        expected_status=400
    )

    data = response.json()

    assert "Поле page имеет минимальную величину 1" in data["message"], (
        f"No 'message' field in 'response.json()'"
    )

#! incorrect location value in filter
def test_invalid_location_filter(
        unauthenticated_api_manager:ApiManager,
        invalid_location       
    ):

    params = invalid_location

    response = unauthenticated_api_manager.movies_api.get_movies(
        params,
        expected_status=400
    )

    data = response.json()

    assert (
    "Каждое значение в поле locations должно быть одним из значений: MSK, SPB"
    in data["message"]
    ), (
    "No 'message' field in 'response.json()'"
    )
