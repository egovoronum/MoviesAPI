import pytest, allure
from utils.time_util import iso_now
from faker import Faker
fake = Faker("ru_RU")
from models.base_models import Movie, ApiError, Genre, Review
from entities.user import User


@allure.title("Проверка доступов к DELETE MOVIE")
@pytest.mark.accesscontrol
@pytest.mark.regression
@pytest.mark.parametrize("user, status", [
    ("super_admin", 200),
    ("admin_user", 403),
    ("common_user", 403),
], ids=["SUPER ADMIN", "ADMIN USER", "COMMON USER"])
def test_access_delete_movie(
    request, super_admin, oneshot_movie_skip_teardown, user, status
    ):

  
        client = request.getfixturevalue(user)
        created_movie = oneshot_movie_skip_teardown

        movie_deleted = False

        try:
            with allure.step("делаем запрос на удаление"):
                delete_response = client.api.movies_api.delete_movie(
                    created_movie.id,
                    expected_status=status
                )

            if status == 200:
                with allure.step("проверяем, что удаленный фильм совпадает с ожидаемым"):
                    movie_deleted = True
                    deleted_movie = delete_response.json()
                    assert deleted_movie["id"] == created_movie.id

            else:
                with allure.step("сверяем ошибку доступа для COMMON_USER с моделью ApiError"):    
                    e = ApiError(**delete_response.json())
                    assert e.error == "Forbidden"
                    assert e.statusCode == 403

        finally:
            with allure.step("ручной teardown"):    
                if not movie_deleted:
                    super_admin.api.movies_api.delete_movie(
                        created_movie.id,
                        expected_status=200
                    )


@allure.title("Проверяем параметризацию фильтров")            
@pytest.mark.regression
class TestParametrizedFilters:
    @pytest.mark.parametrize("filter_parameters", [
        {
            "minPrice": 1,
            "maxPrice": 1000,
        },
        {
            "locations": "MSK"
        },
        {
            "genreId": 1
        }
    ], ids=["PRICE FILTER", "LOCATION FILTER", "GENRE FILTER"])
    def test_parametrized_movie_filters(
            self,
            common_user,
            filter_parameters
        ):

        response = common_user.api.movies_api.get_movies(
            params=filter_parameters,
            expected_status=200
        )


@allure.epic("проверяем получение фильмов, создание фильмов, работу фильтров фильмов")
@pytest.mark.regression
class TestMovies:

    @allure.title("проверяем, что GET несуществующего MOVIE_ID возвращает 404")
    @pytest.mark.regression
    def test_get_404movie(
            self,
            common_user: User,
            invalid_movie_id: int
        ):

        response = common_user.api.movies_api.get_movie(
            invalid_movie_id, 
            expected_status=404
        )

        data = response.json()

        assert "Фильм не найден" in data["message"]
        assert "Not Found" in data["error"]


    @allure.title("проверяем, что GET существующего movie id возвращает 200")
    @pytest.mark.regression
    def test_get_200movie(
            self,
            common_user: User,
            grab_movie: int
        ):

        response = common_user.api.movies_api.get_movie(
            grab_movie,
            expected_status=200
        )
        data = Movie(**response.json())

        assert data.id == grab_movie


    @allure.title("проверяем, что GET списка фильмов дает 200 и живой список")
    @pytest.mark.regression
    def test_get_movies(
            self,
            common_user: User,
            valid_filter_params: dict
        ):

        page_size = valid_filter_params["pageSize"]

        with allure.step("отправляем запрос"):            
            response = common_user.api.movies_api.get_movies(
                params=valid_filter_params, 
                expected_status=200
            )

            data = response.json()
            movies = data["movies"]

        with allure.step("проверяем, что не получили пустой список, сверяем page_size"):
            assert len(movies) > 0, f"Returned empty list"
            assert page_size == data["pageSize"], f"pageSize mismatch"

        with allure.step("доп проверяем, что фильм в списке не пустышка"):
            movie = Movie(**movies[0])
            assert movie.name, "name string is empty"


    @allure.title("проверяем работоспособность фильтров цены")
    @pytest.mark.regression
    def test_get_movies_by_price(
            self,
            common_user: User,
            valid_price_filter: dict
        ):

        with allure.step("отправляем запрос"):
            params = valid_price_filter
            min_price = params["minPrice"]
            max_price = params["maxPrice"]

            response = common_user.api.movies_api.get_movies(
                params=params, 
                expected_status=200
            )
            
            data = response.json()
            movies = data["movies"]

        with allure.step("проверяем работоспособность сортировки, " \
        "каждый ассерт отдельно, т.к проще дебажить"):
            for movie in movies:
                assert movie["price"] >= min_price, (
                    f"Price out of specified range. Look at min_price"
                )
                assert movie["price"] <= max_price, (
                    f"Price out of specified range. Look at max_price"
                )


    @allure.title("проверяем работоспособность сортировки фильмов по возрастанию")
    @pytest.mark.regression
    def test_get_movies_asc(
            self,
            common_user: User,
            asc_filter: dict
        ):

        with allure.step("отправляем запрос с ascending фильтром"):
            response = common_user.api.movies_api.get_movies(
                params=asc_filter,
                expected_status=200
            )


            data = response.json()
            movies = data["movies"]

        with allure.step("проверяем фильмы на соответствие модели"):
            
            for movie in movies:
                Movie(**movie)

            
        with allure.step("проверяем сортировку"):
            previous = "1900-05-26T11:00:15.900Z"

            for movie in movies:
                assert "createdAt" in movie, (f"No createdAt in movie.")
                current = movie["createdAt"]
                assert current >= previous, f"createdAt sorting broken: {current} < {previous}"
                previous = current


    @allure.title("проверяем работоспособность сортировки фильмов по убыванию")
    @pytest.mark.regression
    def test_get_movies_desc(
            self,
            common_user: User,
            desc_filter: dict
        ):

        with allure.step("делаем запрос"):
            response = common_user.api.movies_api.get_movies(
                params=desc_filter,
                expected_status=200
            )

        data = response.json()
        movies = data["movies"]

        with allure.step("проверяем фильмы на соответствие модели"):
            
            for movie in movies:
                Movie(**movie)

        with allure.step("проверяем сортировку"):
            previous = "2500-05-26T11:00:15.900Z"
            
            for movie in movies:
                
                assert "createdAt" in movie, (f"No createdAt in movie.")
                current = movie["createdAt"]
                assert current < iso_now(), f"CreatedAt is > than current time. Double-check."
                assert current <= previous, f"createdAt sorting broken: {current} > {previous}"
                previous = current


@allure.epic("проверка создания и редактирования фильмов")
@pytest.mark.regression
class TestEditMovies:   

    @allure.title("проверка созданного фильма на соответствие модели")
    @pytest.mark.regression
    def test_create_movie(self, create_test_movie):
        with allure.step("сверяем созданный фильм с моделью"):
            Movie(**create_test_movie)

    @allure.title("проверка DELETE MOVIE")
    @pytest.mark.regression
    def test_delete_random_movie(
            self,
            super_admin: User,
            grab_movie: int
        ):

        response = super_admin.api.movies_api.delete_movie(
            grab_movie,
            expected_status=200
        )
        data = response.json()
        print(data)
        assert grab_movie == data["id"]


@allure.epic("проверка жанров")
@pytest.mark.regression
class TestGenres:

    @allure.title("проверка GET **списка** жанров")
    @pytest.mark.regression
    def test_get_genres(
            self,
            get_genres: dict
        ):

        genres = get_genres

        with allure.step("сверяем каждый жанр в словаре с моделью"):    
            for genre in genres:
                Genre(**genre)

    @allure.title("получаем 1 жанр и сверяем с моделью")
    @pytest.mark.regression
    def test_get_random_genre(
            self,
            common_user: User,
            random_genre: int,
        ):

        with allure.step("делаем запрос"):
            response = common_user.api.movies_api.get_genre(
                random_genre,
                expected_status=200
            )

        with allure.step("сверяем жанр с моделью"):
            Genre(**response.json())


    @allure.title("проверяем создание жанра")
    @pytest.mark.regression
    def test_create_random_genre(
            self,
            super_admin: User,
            genre_data:dict
        ):

        with allure.step("делаем запрос"):
            response = super_admin.api.movies_api.create_genre(
                genre_data,
                expected_status=201
            )

        with allure.step("сверяем жанр с моделью"):
            data = Genre(**response.json())
            genre_data["id"] = data.id


    @allure.title("проверяем удаление рандомного жанра")
    @pytest.mark.regression
    def test_delete_random_genre(
            self,
            super_admin: User,
            random_genre: int
        ):

        genre_id = random_genre

        with allure.step("делаем запрос"):
            response = super_admin.api.movies_api.delete_genre(
                genre_id,
                expected_status=200
            )

        with allure.step("сверяем ответ с моделью"):
            Genre(**response.json())


@allure.epic("тестирование жанров")
@pytest.mark.regression
class TestReviews:

    @allure.title("проверка POST обзора на фильм")
    @pytest.mark.regression
    def test_post_movie_review_as_admin(
            self,
            admin_user: User,
            movie_id: int,
            generate_review: dict
        ):

        with allure.step("запрос на создание со словарем из фикстуры"):    
            response = admin_user.api.movies_api.post_review(
                movie_id = movie_id,
                data = generate_review,
                expected_status=201
            )

        with allure.step("сверка с моделью"):    
            data = Review(**response.json())

        with allure.step("сверяем текст и рейтинг созданного обзора с полученным словарем от фикстуры"):
            assert generate_review["text"] == data.text
            assert generate_review["rating"] == data.rating

        with allure.step("передача параметров созданного обзора в teardown фикстуры"):    
            generate_review["movieId"] = movie_id
            generate_review["userId"] = data.userId

    @allure.title("проверка POST отзыва с USER правами")
    @pytest.mark.regression
    def test_movie_review_as_user(
            self,
            common_user: User,
            movie_id: int,
            generate_review: dict
        ):

        with allure.step("отправляем запрос"):
            response = common_user.api.movies_api.post_review(
                movie_id=movie_id,
                data = generate_review,
                expected_status=201
            )

        with allure.step("сверяем ответ с моделью"):
            data = Review(**response.json())

        with allure.step("передаем данные в teardown фикстуры"):
            generate_review["movieId"] = movie_id
            generate_review["userId"] = data.userId


@allure.description("""
тест не работает так как надо,
скипаю пока
""")
@pytest.mark.skip
def test_patch_random_movie(
        super_admin: User,
        grab_movie: int, 
        patch_movie: dict
    ):

    response = super_admin.api.movies_api.patch_movie(
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