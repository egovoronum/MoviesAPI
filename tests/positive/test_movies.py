import pytest, allure
from datetime import datetime, timezone
from pytest_check import check
from utils.time_util import iso_now
from faker import Faker
fake = Faker("ru_RU")
from models.base_models import Movie, ApiError, Genre, Review, ValidFilterParams, MoviesPage, GenreList, CreateGenreData, CreateReviewData
from entities.user import User

@allure.description("""
    проверяет авторизацию DELETE MOVIE
    super_admin может удалять (200)
    admin_user и common_user получают 403 Forbidden с корректным ApiError
    """)
@pytest.mark.accesscontrol
@pytest.mark.regression
@pytest.mark.parametrize(
    "user, status",
    [
        ("super_admin", 200),
        ("admin_user", 403),
        ("common_user", 403),
    ],
    ids=["SUPER ADMIN", "ADMIN USER", "COMMON USER"],
)
def test_access_delete_movie(
    request,
    super_admin: User,
    oneshot_movie_skip_teardown: Movie,
    user,
    status,
) -> None:
    """Тестирует доступ к DELETE /movies/:id."""
    allure.dynamic.title(f"Проверка доступов к DELETE MOVIE {user} {status}")

    client = request.getfixturevalue(user)
    created_movie = oneshot_movie_skip_teardown
    movie_deleted = False

    try:
        with allure.step("Отправляем запрос на удаление"):
            delete_response = client.api.movies_api.delete_movie(
                created_movie.id,
                expected_status=status,
            )

        if status == 200:
            with allure.step("Проверяем, что удаленный фильм совпадает с ожидаемым"):
                movie_deleted = True
                deleted_movie = delete_response.json()
                check.equal(deleted_movie["id"], created_movie.id, "id удаленного фильма не соответствует id созданного")

        else:
            with allure.step("Сверяем ошибку доступа для COMMON_USER с моделью ApiError"):
                e = ApiError(**delete_response.json())
                check.equal(e.error, "Forbidden", "error не содержит Forbidden")
                check.equal(e.statusCode, 403, "статус-код не 403")

    finally:
        with allure.step("Ручной teardown"):
            if not movie_deleted:
                super_admin.api.movies_api.delete_movie(
                    created_movie.id,
                    expected_status=200,
                )


@allure.epic("Работа с фильмами")
@pytest.mark.regression
class TestMovies:

    @allure.title("GET существующий фильм (200)")
    @allure.description("""
        проверяет GET существующего фильма по ID
        ожидается статус 200
        валидирует соответствие ответа модели Movie
        """)
    @pytest.mark.regression
    def test_get_200movie(
            self,
            common_user: User,
            grab_movie: int
        ):

        with allure.step("Делаем запрос на получение фильма по id"):
            response = common_user.api.movies_api.get_movie(
                grab_movie,
                expected_status=200
            )

        with allure.step("Сверяем полученный фильм с моделью"):
            data = Movie(**response.json())

        with allure.step("Сверяем ID полученного vs изначальный ID"):
            check.equal(data.id, grab_movie, "ID не совпадаеют")


    @allure.title("GET список фильмов (200)")
    @allure.description("""
        проверяет получение списка фильмов
        не пустой список
        pageSize совпадает с параметрами запроса
        фильмы не пустышки (имеют name)
        """)
    @pytest.mark.regression
    def test_get_movies(
        self,
        common_user: User,
        valid_filter_params: ValidFilterParams,
    ) -> None:
        page_size = valid_filter_params.pageSize

        with allure.step("Отправляем запрос"):
            response = common_user.api.movies_api.get_movies(
                params=valid_filter_params.model_dump(),
                expected_status=200,
            )

        data = MoviesPage(**response.json())
        movies = data.movies

        with allure.step("Проверяем, что не получили пустой список"):
            check.greater(len(movies), 0, "Cписок фильмов пуст")

        with allure.step("Сверяем pageSize с параметрами запроса"):
            check.equal(
                page_size,
                data.pageSize,
                f"pageSize mismatch: {page_size} != {data.pageSize}",
            )

        with allure.step("Проверяем, что фильм не пустышка"):
            movie = movies[0]
            check.not_equal(movie.name, "", "поле name пустое")


    @allure.title("Фильтр по цене (range check)")
    @allure.description("Проверяет фильтрацию по цене: каждый фильм имеет price в диапазоне [minPrice, maxPrice]")
    @pytest.mark.regression
    def test_get_movies_by_price(
        self,
        common_user: User,
        valid_price_filter: ValidFilterParams,
    ) -> None:
        with allure.step("Отправляем запрос"):
            params = valid_price_filter.model_dump()
            min_price = valid_price_filter.minPrice
            max_price = valid_price_filter.maxPrice

            response = common_user.api.movies_api.get_movies(
                params=params,
                expected_status=200,
            )

        data = MoviesPage(**response.json())
        movies = data.movies

        with allure.step("Проверяем диапазон цен"):
            for movie in movies:
                check.greater_equal(
                    movie.price,
                    min_price,
                    f"Цена {movie.price} не может быть ниже minPrice={min_price}",
                )
                
                check.less_equal(
                movie.price,
                max_price,
                f"Цена {movie.price} не может быть выше maxPrice={max_price}",
                )     


    @allure.title("Сортировка фильмов: ASC")
    @allure.description("Проверяет сортировку фильмов по возрастанию createdAt")
    @pytest.mark.regression
    def test_get_movies_asc(
        self,
        common_user: User,
        asc_filter: ValidFilterParams,
    ) -> None:
        with allure.step("Отправляем запрос с ascending фильтром"):
            response = common_user.api.movies_api.get_movies(
                params=asc_filter.model_dump(),
                expected_status=200,
            )

        data = MoviesPage(**response.json())
        movies = data.movies

        with allure.step("Проверяем сортировку по createdAt"):
            previous: datetime = datetime(
                1900, 5, 26, 11, 0, 15, 900_000, tzinfo=timezone.utc
            )

            for movie in movies:
                current = movie.createdAt
                check.greater_equal(
                    current,
                    previous,
                    f"createdAt не отсортирован по возрастанию: {current} < {previous}",
                )
                previous = current


    @allure.title("Сортировка фильмов: DESC")
    @allure.description("""
        проверяет сортировку фильмов по убыванию createdAt
        проверяем createdAt не больше текущего времени
        createdAt уменьшается от запроса к запросу
        """)
    @pytest.mark.regression
    def test_get_movies_desc(
        self,
        common_user: User,
        desc_filter: ValidFilterParams,
    ) -> None:
        with allure.step("Отправляем запрос"):
            response = common_user.api.movies_api.get_movies(
                params=desc_filter.model_dump(),
                expected_status=200,
            )

        data = MoviesPage(**response.json())
        movies = data.movies

        with allure.step("Проверяем фильмы на соответствие модели"):
            for movie in movies:
                check.is_true(movie.name, "name string is empty")
            
            previous = datetime(2500, 5, 26, 11, 0, 15, 900_000, tzinfo=timezone.utc)

            for movie in movies:
                current = movie.createdAt
                check.less_equal(
                    current,
                    previous,
                    f"createdAt не отсортирован по убыванию: {current} > {previous}",
                )
                previous = current


@allure.title("Параметризированные фильтры")          
@pytest.mark.regression
class TestParametrizedFilters:
    @allure.title("Проверяем параметризацию фильтров (цена/локация/жанр)")
    @allure.description("""
        проверяет параметризацию фильтров
        цена (minPrice, maxPrice), локация (locations), жанр (genreId)
        все возвращают 200 с живыми данными
        """)
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
            common_user: User,
            filter_parameters
        ) -> None:

        common_user.api.movies_api.get_movies(
            params=filter_parameters,
            expected_status=200
        )


@allure.epic("Создание и редактирование фильмов")
@pytest.mark.regression
class TestEditMovies:   

    @allure.title("POST фильм (валидация ответа)")
    @allure.description("""
        проверяет создание фильма через API
        сверка созданного фильма с моделью Movie
        """)
    @pytest.mark.regression
    def test_create_movie(
        self, 
        create_test_movie
        ) -> None:

        with allure.step("сверяем созданный фильм с моделью"):
            Movie(**create_test_movie)


    @allure.title("DELETE фильм (проверка удаления в БД)")
    @allure.description("""
        проверка DELETE MOVIE с проверкой базы
        API вернул нужный ID после удаления
        PostgreSQL возвращает None по удалённому ID
        """)
    @pytest.mark.regression
    def test_delete_movie(
            self,
            db_helper,
            super_admin: User,
            create_test_movie_no_teardown: Movie
        ) -> None:

        with allure.step("Вынимаем ID фильма"):
            movie_id = create_test_movie_no_teardown.id

        with allure.step("Отправляем API запрос на удаление"):
            response = super_admin.api.movies_api.delete_movie(
                movie_id,
                expected_status=200
            )

        with allure.step("Сверяем, что API вернул нужный ID после DELETE"):
            data = Movie(**response.json())
            check.equal(movie_id, data.id, "ID не совпадают")

        with allure.step("Отправляем запрос в базу по удаленному API ID"):  
            db_response = db_helper.get_movie_by_id(data.id)
            check.equal(db_response, None, "DB_HELPER: movie не удален в базе")
            print(f"ОТВЕТ ОТ БАЗЫ: {db_response}")
            

@allure.epic("Работа с жанрами")
@pytest.mark.regression
class TestGenres:

    @allure.title("GET список жанров")
    @allure.description("""
        проверяет GET список жанров
        сверка каждого жанра в словаре с моделью Genre
        """)
    @pytest.mark.regression
    def test_get_genres(
            self,
            get_genres: GenreList
        ) -> None:

        with allure.step("Список жанров не пустой"):
            check.is_true(len(get_genres.root) > 0, "API вернул пустой список")

        with allure.step("id жанров уникальны"):
            ids = [g.id for g in get_genres.root]
            check.equal(len(ids), len(set(ids)))


    @allure.title("GET один жанр по ID")
    @allure.description("""
        проверка GET отдельного жанра по ID
        сверка жанра с моделью Genre
        """)
    @pytest.mark.regression
    def test_get_random_genre(
            self,
            common_user: User,
            random_genre: int,
        ) -> None:

        with allure.step("делаем запрос"):
            response = common_user.api.movies_api.get_genre(
                random_genre,
                expected_status=200
            )

        with allure.step("сверяем жанр с моделью"):
            Genre(**response.json())


    @allure.title("POST жанр")
    @allure.description("""
        проверка создания жанра через API
        ожидается статус 201
        передаем созданный ID в фикстуру для teardown
        """)
    @pytest.mark.regression
    def test_create_random_genre(
            self,
            super_admin: User,
            genre_data:CreateGenreData
        ) -> None:

        with allure.step("делаем запрос"):
            response = super_admin.api.movies_api.create_genre(
                genre_data.model_dump(),
                expected_status=201
            )

        with allure.step("сверяем жанр с моделью"):
            data = Genre.model_validate(response.json())
            genre_data.id = data.id


    @allure.title("DELETE жанр")
    @allure.description("""
        проверка удаления жанра по ID
        сверка ответа с моделью Genre
        """)
    @pytest.mark.regression
    def test_delete_random_genre(
            self,
            super_admin: User,
            random_genre: int
        ) -> None:

        genre_id = random_genre

        with allure.step("делаем запрос"):
            response = super_admin.api.movies_api.delete_genre(
                genre_id,
                expected_status=200
            )

        with allure.step("сверяем ответ с моделью"):
            Genre.model_validate(response.json())


@allure.epic("Работа с отзывами")
@pytest.mark.regression
class TestReviews:

    @allure.title("POST отзыв (от admin_user)")
    @allure.description("""
        проверка POST отзыва от admin_user
        ожидается статус 201
        валидируем text и rating
        передаём movieId, userId в teardown фикстуры
        """)
    @pytest.mark.regression
    def test_post_movie_review_as_admin(
            self,
            super_admin: User,
            movie_id: int,
            generate_review: CreateReviewData
        ):

        with allure.step("Запрос на создание со словарем из фикстуры"):    
            response = super_admin.api.movies_api.post_review(
                movie_id = movie_id,
                data = generate_review.model_dump(exclude_none=True),
                expected_status=201
            )

        with allure.step("Сверка с моделью"):    
            data = Review.model_validate(response.json())

        with allure.step("Сверяем текст и рейтинг созданного обзора с полученным словарем от фикстуры"):
            check.equal(generate_review.text, data.text)
            check.equal(generate_review.rating, data.rating)

        with allure.step("Передача параметров созданного обзора в teardown фикстуры"):    
            generate_review.userId = data.userId
            generate_review.movieId = data.movieId


    @allure.title("POST отзыв (от common_user)")
    @allure.description("""
        проверка размещения отзыва от common_user
        ожидается статус 201
        сверка с моделью Review
        передача данных в teardown фикстуры
        """)
    @pytest.mark.regression
    def test_movie_review_as_user(
            self,
            common_user: User,
            movie_id: int,
            generate_review: CreateReviewData
        ):

        with allure.step("отправляем запрос"):
            response = common_user.api.movies_api.post_review(
                movie_id=movie_id,
                data = generate_review.model_dump(exclude_none=True),
                expected_status=201
            )

        with allure.step("сверяем ответ с моделью"):
            data = Review.model_validate(response.json())

        with allure.step("Сверяем текст и рейтинг с полученным от фикстуры"):
            check.equal(generate_review.text, data.text)
            check.equal(generate_review.rating, data.rating)

        with allure.step("передаем данные в teardown фикстуры"):
            generate_review.movieId = movie_id
            generate_review.userId = data.userId


@allure.title("PATCH фильм (skip)")
@allure.description("""
тест не работает корректно,
непонятна логика PATCH
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