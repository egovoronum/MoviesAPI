import pytest, allure
from clients.api_manager import ApiManager 
from models.base_models import CreatedUser, LoggedInUser, ApiError

class TestUsers:

    def test_create_user(self, super_admin, create_user_data: dict):
        response = super_admin.api.user_api.create_user(create_user_data).json()

        assert response.get('id') and response['id'] != '', "ID должен быть не пустым"
        assert response.get('email') == create_user_data['email']
        assert response.get('fullName') == create_user_data['fullName']
        assert response.get('verified') is True

    def test_get_user_by_locator(self, super_admin, create_user_data: dict):
        created_user_response = super_admin.api.user_api.create_user(create_user_data).json()
        response_by_id = super_admin.api.user_api.get_user_info(created_user_response['id']).json()
        response_by_email = super_admin.api.user_api.get_user_info(create_user_data['email']).json()

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.get('id') and response_by_id['id'] != '', "ID должен быть не пустым"
        assert response_by_id.get('email') == create_user_data['email']
        assert response_by_id.get('fullName') == create_user_data['fullName']
        assert response_by_id.get('verified') is True

    @allure.title("проверка регистрации нового пользователя")
    @pytest.mark.regression
    def test_register_user(
            self,
            unauthenticated_api_manager: ApiManager,
            test_user: dict
        ):

        with allure.step("делаем запрос на создание"):
            response = unauthenticated_api_manager.auth_api.register_user(test_user)

        with allure.step("сверяем с моделью models.base_models CreatedUser"):
            data = CreatedUser(**response.json())

            assert data.id != '', "ответ должен вернуть ID"
            assert data.email == test_user["email"], "поле email не совпадает"
            assert data.fullName == test_user["fullName"], "поле fullName не совпадает"

        with allure.step("передаем id в teardown фикстуры"):
            test_user["id"] = data.id

    @allure.title("проверка логина супер админа")
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
        assert "SUPER_ADMIN" in data.user.roles, "вернувшийся user не SUPER_ADMIN"


    @allure.title("проверка получения информации о юзере")
    @pytest.mark.accesscontrol
    @pytest.mark.regression
    @pytest.mark.parametrize("user, status", [
    ("admin_user", 403),
    ("common_user", 403),
], ids=["ADMIN USER", "COMMON USER"])
    def test_get_user_info(
            self,
            request,
            user,
            status,
            get_user: int
        ):

        client = request.getfixturevalue(user)

        with allure.step(f"делаем запрос от лица {client}"):    
            response = client.api.user_api.get_user_info(
                get_user, 
                expected_status=status
            )

        if status != 200:
            with allure.step(f"Статус код не 200. Сверяем ошибку доступа {client} с моделью ApiError"):    
                e = ApiError(**response.json())
                assert e.error == "Forbidden", "неожиданное сообщение об ошибке, ожидалось 403"
                assert e.statusCode == 403, "статуск код не 403"

        if status == 200:
            with allure.step(f"Логин из под {client}. Статус код 200. Сверяем с моделью"):
                data = LoggedInUser(**response.json())
                assert client in data.user.roles, "роль в ответе не совпадает с клиентом"


    def test_delete_user(
            self,
            admin_api_manager: ApiManager,
            test_user_deletion: str):

        response = admin_api_manager.user_api.delete_user(
            test_user_deletion,
            expected_status=200
        )


