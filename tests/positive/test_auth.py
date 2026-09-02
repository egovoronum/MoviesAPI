from clients.api_manager import ApiManager

class TestUser:

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


def test_register_user(
        unauthenticated_api_manager: ApiManager,
        test_user: dict
    ):

    response = unauthenticated_api_manager.auth_api.register_user(test_user)
    
    data = response.json()

    test_user["id"] = data["id"]

    assert data["email"] == test_user["email"]
    assert "id" in data
    assert "USER" in data["roles"]


def test_admin_login(
        unauthenticated_api_manager: ApiManager,
        admin_login: dict
    ):

    response = unauthenticated_api_manager.auth_api.login_user(
        admin_login,
        expected_status=200
    )

    data = response.json()


def test_get_user_info(
        unauthenticated_api_manager: ApiManager,
        get_user: int
    ):

    response = unauthenticated_api_manager.user_api.get_user_info(
        get_user, 
        expected_status=401
    )

    data = response.json()


def test_delete_user(
        admin_api_manager: ApiManager,
        test_user_deletion: str):

    response = admin_api_manager.user_api.delete_user(
        test_user_deletion,
        expected_status=200
    )

def test_get_user_by_id_common_user(common_user):
    common_user.api.user_api.get_user_info(common_user.email, expected_status=403)

