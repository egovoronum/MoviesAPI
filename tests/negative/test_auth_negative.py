import pytest, allure
from models.base_models import ApiError

@allure.epic("Негативная проверка AUTH API")
class TestNegativeAuthAPI:
    @allure.title("Проверка доступа к информации о юзере: ожидается отказ")
    @allure.description("""
    проверяем, что admin_user имеет доступ к просмотру /user по ID 
    проверяем, что common_user не имеет доступа к просмотру /user по ID
    проверяем, что сообщение об ошибке возвращает 403 и Forbidden
    """)
    @pytest.mark.accesscontrol
    @pytest.mark.regression
    @pytest.mark.parametrize("user, status", [
    ("super_admin", 200),
    ("admin_user", 200),
    ("common_user", 403),
], ids=["SUPER ADMIN", "ADMIN USER", "COMMON USER"])
    def test_get_user_info_access_denied(
            self,
            request,
            user,
            status,
            get_user: int
        ):

        client = request.getfixturevalue(user)

        with allure.step(f"делаем запрос от лица {user}"):    
            response = client.api.user_api.get_user_info(
                get_user, 
                expected_status=status
            )

        if status != 200:
            with allure.step(f"Сверяем ошибку доступа {user} с моделью ApiError"):    
                e = ApiError(**response.json())
                assert e.error == "Forbidden", "неожиданное сообщение об ошибке, ожидалось 403"
                assert e.statusCode == 403, "статус код не 403"