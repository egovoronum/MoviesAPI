from clients.api_manager import ApiManager

#* Test registration and teardown
def test_register_user(api_manager: ApiManager, test_user: dict):
    
    register_data = test_user["register_data"]

    response = api_manager.auth_api.register_user(register_data)
    data = response.json()
    
    test_user["id"] = data["id"]

    assert data["email"] == register_data["email"]
    assert "id" in data
    assert "USER" in data["roles"]

#* login as ADMIN
def test_admin_login(api_manager: ApiManager, admin_login: dict):

    response = api_manager.auth_api.login_user(admin_login)
    data = response.json()

#* Test get user info as an unauthenticated user
def test_get_user_info(unauthenticated_api_manager: ApiManager, get_user: str):

    response = unauthenticated_api_manager.user_api.get_user_info(get_user, expected_status=401)
    data = response.json()
