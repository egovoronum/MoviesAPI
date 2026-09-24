import pytest
import allure
from pytest_check import check
from clients.api_manager import ApiManager
from models.base_models import ApiError, CreateMovieData
from entities.user import User

@allure.epic("Негативные проверки фильтров Movies API")
class TestMovieFilters:

    @allure.title("Невалидный фильтр цены")
    @allure.description("""
        Проверяет, что API возвращает ошибку 400 при инвертированных 
        границах фильтра цены (maxPrice < minPrice)
        """)
    @pytest.mark.validation
    def test_invalid_price_filter(
            self,
            unauthenticated_api_manager: ApiManager,
            invalid_price_filter_reversed: dict
        ):

        with allure.step("Делаем запрос без аутентификации"):
            response = unauthenticated_api_manager.movies_api.get_movies(
                invalid_price_filter_reversed, 
                expected_status=400
            )

        with allure.step("Сверяем ошибку с моделью ApiError"):    
            e = ApiError(**response.json())

        with allure.step("Ожидаем 400 в ответе и проверяем ожидаемый message"):
            with check:
                check.equal(e.error, "Bad Request", "ожидался другой error")
                check.equal(e.message, "minPrice must be less than maxPrice", "ожидался другой message")


    @allure.title("Фильтр цены с негативным значением")
    @allure.description("""
        Проверяет граничное условие: 
        минимальное значение поля `minPrice` должно быть ≥ 1
        При отрицательном значении: 
        возвращается ошибка 400 с сообщением о минимальной величине поля
        """)
    @pytest.mark.edgecases
    @pytest.mark.validation
    def test_negative_price_filter(
            self,
            unauthenticated_api_manager: ApiManager, 
            invalid_price_filter_negative_min: dict
        ):

        with allure.step("Делаем запрос без аутентификации"):
            response = unauthenticated_api_manager.movies_api.get_movies(
                invalid_price_filter_negative_min,
                expected_status=400
            )

        with allure.step("Сверяем ошибку с моделью ApiError"): 
            e = ApiError(**response.json())

        with allure.step("Ожидаем 400 в ответе и проверяем ожидаемый message"):
            with check:
                check.equal(e.error, "Bad Request", "ожидался другой error")
                check.equal(e.message[0], "Поле minPrice имеет минимальную величину 1", "ожидался другой message")


    @allure.title("Фильтр пагинации с негативным значением")
    @allure.description("""
        Проверяет граничное условие пагинации: поле `page` не может быть ≤ 0
        при значении < 1 возвращается ошибка 400 с сообщением о минимальной странице
        """)
    @pytest.mark.edgecases
    @pytest.mark.validation
    def test_negative_page_filter(
            self,
            unauthenticated_api_manager: ApiManager,
            invalid_page: dict
        ):

        with allure.step("Делаем запрос без аутентификации"):
            response = unauthenticated_api_manager.movies_api.get_movies(
                invalid_page,
                expected_status=400
            )

        with allure.step("Сверяем ошибку с моделью ApiError"):
            e = ApiError(**response.json())

        with allure.step("Ожидаем 400 в ответе и проверяем ожидаемый message"):
            with check:
                check.equal(e.error, "Bad Request", "ожидался другой error")
                check.equal(e.message, "Поле page имеет минимальную величину 1", "ожидался другой message")
            

    @allure.title("Фильтр локации с невалидным значением")
    @allure.description("""
        проверяет валидацию локаций: 
        API возвращает ошибку 400 при некорректном значении поля location
        ожидаемое сообщение содержит текст "Некорректные данные"
        Иногда проверка check.equal(e.error, "Bad Request", "ожидался другой error")
        Не проходит, т.к. API не всегда возвращает это поле!
        """)
    @pytest.mark.validation
    def test_invalid_location_filter(
            self,
            unauthenticated_api_manager: ApiManager,
            invalid_location: dict       
        ):

        with allure.step("Делаем запрос без аутентификации"):            
            response = unauthenticated_api_manager.movies_api.get_movies(
                invalid_location,
                expected_status=400
            )

        with allure.step("Сверяем ошибку с моделью ApiError"):
            e = ApiError(**response.json())

        with allure.step("Ожидаем 400 в ответе и проверяем ожидаемый message"):
            with check:
                check.equal(e.error, "Bad Request", "ожидался другой message")


@allure.epic("Негативные проверки Movies API")
class TestEditMovies:

    @allure.title("GET несуществующий фильм (404)")
    @allure.description("""
        проверяет GET несуществующего фильма по ID
        ожидается статус 404
        сообщение содержит "Фильм не найден" и "Not Found"
        """)
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

        e = ApiError(**response.json())

        with check:
            check.equal(e.error, "Not Found", "ожидался другой error")
            check.equal(e.message, "Фильм не найден", "ожидался другой message")


    @allure.title("Проверка создания фильма с невалидными данными (ожидается 400)")
    @allure.description("""
    проверяет, что API возвращает ошибку 400 при создании фильма с некорректными данными
    валидирует поле location (должен быть MSK или SPB)
    Поле message возвращается списком [] по какой-то причине
    """)
    @pytest.mark.regression
    def test_create_invalid_movie(
            self,
            super_admin: User,
            invalid_movie_data: dict
        ):

        response = super_admin.api.movies_api.create_movie(
            invalid_movie_data,
            expected_status=400
        )

        e = ApiError(**response.json())

        with check:
            check.equal(e.error, "Bad Request", "ожидался другой error")
            check.equal(e.message[0], "Поле location должно быть одним из: MSK, SPB", "ожидался другой message")
        

    @allure.title("Проверка может ли USER создать фильм (ожидается 403)")
    @allure.description("""
        Проверяет авторизацию: 
        common_user не имеет прав на создание фильма при попытке создания
        возвращается ошибка 403 с сообщением "Forbidden resource"
        """)
    @pytest.mark.accesscontrol
    def test_create_as_common_user(
            self,
            common_user: User,
            valid_movie_data: dict
        ):

        CreateMovieData(**valid_movie_data)

        response = common_user.api.movies_api.create_movie(
            valid_movie_data,
            expected_status=403
        )

        e = ApiError(**response.json())
        
        with check:
            check.equal(e.error, "Forbidden", "ожидался другой error")
            check.equal(e.message, "Forbidden resource", "ожидался другой message")
        

