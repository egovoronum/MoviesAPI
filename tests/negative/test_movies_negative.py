from clients.api_manager import ApiManager

class TestMovieFilters:

    def test_invalid_price_filter(
            self,
            unauthenticated_api_manager: ApiManager,
            invalid_price_filter_reversed: dict
        ):

        response = unauthenticated_api_manager.movies_api.get_movies(
            invalid_price_filter_reversed, 
            expected_status=400
        )

        data = response.json()
        
        assert "minPrice must be less than maxPrice" in data["message"]


    def test_negative_price_filter(
            self,
            unauthenticated_api_manager: ApiManager, 
            invalid_price_filter_negative_min: dict
        ):

        response = unauthenticated_api_manager.movies_api.get_movies(
            invalid_price_filter_negative_min,
            expected_status=400
        )

        data = response.json()

        assert "Поле minPrice имеет минимальную величину 1" in data["message"]


    def test_negative_page_filter(
            self,
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


    def test_invalid_location_filter(
            self,
            unauthenticated_api_manager: ApiManager,
            invalid_location: dict       
        ):

        response = unauthenticated_api_manager.movies_api.get_movies(
            invalid_location,
            expected_status=400
        )

        data = response.json()

        assert (
        "Некорректные данные"
        in data["message"]
        )

class TestEditMovies:

    def test_create_invalid_movie(
            self,
            admin_api_manager: ApiManager,
            invalid_movie_data: dict
        ):

        response = admin_api_manager.movies_api.create_movie(
            invalid_movie_data,
            expected_status=400
        )

        data = response.json()

        assert "Поле location должно быть одним из: MSK, SPB" in data["message"]
        assert "Bad Request" in data["error"]

    def test_create_as_common_user(
            self,
            common_user,
            valid_movie_data
        ):

        response = common_user.api.movies_api.create_movie(
            valid_movie_data,
            expected_status=403
        )

        data = response.json()

        assert "Forbidden" in data["error"]
