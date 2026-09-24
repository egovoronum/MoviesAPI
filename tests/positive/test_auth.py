import pytest
import allure
from pytest_check import check
from clients.api_manager import ApiManager 
from models.base_models import CreatedUser, LoggedInUser, ApiError
from uuid import UUID
from entities.user import User

@allure.epic("Позитивные проверки UsersAPI")
class TestUsers:

    @allure.title("Создание пользователя")
    @allure.description("""
        проверяет корректность создания пользователя супер-админом
        валидирует поля id, email, fullName, verified в ответе CreatedUser
        """)
    @pytest.mark.regression
    def test_create_user(self, super_admin, create_user_data: dict):

        with allure.step("Делаем запрос на создание юзера"):    
            response = super_admin.api.user_api.create_user(create_user_data).json()

        with allure.step("Валидируем ответ по модели CreatedUser"):
            validated_response = CreatedUser(**response)

        with allure.step("проверяем поля id, email, fullName, verified"):
            with check:
                check.not_equal(validated_response.id, "", "ID не должен быть пустым")
                check.equal(validated_response.email, create_user_data['email'], "email не совпадает")
                check.equal(validated_response.fullName, create_user_data['fullName'], "fullName не совпадает")
                check.equal(validated_response.verified, True, "поле verified не True")
                

    @allure.title("Получение информации о пользователе по идентификатору и email")
    @allure.description("""
        проверяет консистентность ответов /user/{id} и /user/{email}
        подтверждает совпадение id, email, fullName и verified между обоими запросами
        """)
    @pytest.mark.regression
    def test_get_user_by_locator(self, super_admin, create_user_data: dict):

        with allure.step("Делаем запросы на создание юзера и GET по id и email"):
            created_user_response = super_admin.api.user_api.create_user(create_user_data).json()
            response_by_id = super_admin.api.user_api.get_user_info(created_user_response['id']).json()
            response_by_email = super_admin.api.user_api.get_user_info(create_user_data['email']).json()

        with allure.step("""
        Проверяем: id совпадают, email совпадают, fullName совпадают, verified = True
        """):
            assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
            assert response_by_id.get('id') and response_by_id['id'] != '', "ID должен быть не пустым"
            assert response_by_id.get('email') == create_user_data['email']
            assert response_by_id.get('fullName') == create_user_data['fullName']
            assert response_by_id.get('verified') is True


    @allure.title("Регистрация нового пользователя")
    @allure.description("""
        проверяет успешную регистрацию без авторизации
        валидирует возвращение id, email, fullName через CreatedUser
        передаёт id в фикстуру для teardown
        """)
    @pytest.mark.regression
    def test_register_user(
            self,
            unauthenticated_api_manager: ApiManager,
            test_user: dict
        ):

        with allure.step("Делаем запрос на создание"):
            response = unauthenticated_api_manager.auth_api.register_user(test_user)

        with allure.step("Сверяем с моделью models.base_models CreatedUser"):
            data = CreatedUser(**response.json())

            assert data.id != '', "ответ должен вернуть ID"
            assert data.email == test_user["email"], "поле email не совпадает"
            assert data.fullName == test_user["fullName"], "поле fullName не совпадает"

        with allure.step("Передаем id в teardown фикстуры"):
            test_user["id"] = data.id

    @allure.title("Логин супер-админа")
    @allure.description("""
        проверяет успешный вход с ролью SUPER_ADMIN
        валидирует поля user.email и наличие роли SUPER_ADMIN в ответе
        """)
    @pytest.mark.regression
    def test_admin_login(
            self,
            unauthenticated_api_manager: ApiManager,
            admin_login: dict
        ):

        with allure.step("отправляем запрос с данными супер админа"):
            response = unauthenticated_api_manager.auth_api.login_user(
                admin_login,
                expected_status=201
            )
            
        with allure.step ("сверяем с моделью"):
            data = LoggedInUser(**response.json())

        assert admin_login["email"] == data.user.email, "поле user не совпадает с данными логина админа"
        assert "SUPER_ADMIN" in data.user.roles, "user не имеет прав SUPER_ADMIN"


    @allure.title("Получение информации о пользователе по id")
    @allure.description("""
        проверяет доступ к /user/{id} для admin_user (200 OK)
        проверяет отказ common_user с ошибкой 403 Forbidden и корректное ApiError сообщение
        """)
    @pytest.mark.accesscontrol
    @pytest.mark.regression
    @pytest.mark.parametrize("user, status", [
    ("admin_user", 200),
    ("common_user", 403),
], ids=["ADMIN USER", "COMMON USER"])
    def test_get_user_info(
            self,
            request,
            user: User,
            status,
            get_user: UUID
        ):

        client = request.getfixturevalue(user)

        with allure.step(f"Делаем запрос от лица {user}"):    
            response = client.api.user_api.get_user_info(
                get_user, 
                expected_status=status
            )

        if status != 200:
            with allure.step(f"Статус код не 200. Сверяем ошибку доступа {user} с моделью ApiError"):    
                e = ApiError(**response.json())
                assert e.error == "Forbidden", "неожиданное сообщение об ошибке, ожидалось 403"
                assert e.statusCode == 403, "статуск код не 403"


    @allure.title("Удаление пользователя через API (сверка с Postgres)")
    @allure.description("""
        проверяет удаление пользователя супер-админом по id
        подтверждает удаление в базе (PostgreSQL возвращает None)
        """)
    @pytest.mark.regression
    def test_delete_user(
            self,
            db_helper,
            super_admin: User,
            oneshot_user_id: UUID):

        with allure.step("""
        Делаем запрос на удаление id, полученного от фикстуры oneshot_user_id через API
        """):    
            super_admin.api.user_api.delete_user(
                str(oneshot_user_id),
                expected_status=200
            )

        with allure.step("Проверяем, что Postgres вернул None по запросу в базу"):
            db_response = db_helper.get_user_by_id(oneshot_user_id)
            assert db_response is None, "DB_HELPER: юзер не удален в базе"


