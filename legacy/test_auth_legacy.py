
# class TestAuthAPI:
    # def test_register_user(self, requester, test_user):
    #     """
    #     Тест на регистрацию пользователя.
    #     """
    #     response = requester.send_request(
    #         method="POST",
    #         endpoint=REGISTER_ENDPOINT,
    #         data=test_user,
    #         expected_status=201
    #     )
    #     response_data = response.json()
    #     assert response_data["email"] == test_user["email"], "Email не совпадает"
    #     assert "id" in response_data, "ID пользователя отсутствует в ответе"
    #     assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
    #     assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    # def test_register_and_login_user(self, requester, registered_user):
    #     """
    #     Тест на регистрацию и авторизацию пользователя.
    #     """
    #     login_data = {
    #         "email": registered_user["email"],
    #         "password": registered_user["password"]
    #     }
    #     response = requester.send_request(
    #         method="POST",
    #         endpoint=LOGIN_ENDPOINT,
    #         data=login_data,
    #         expected_status=201
    #     )
    #     response_data = response.json()
    #     assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
    #     assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"



    # def test_register_temp_user(self, test_user): # testing registration with a temp user
    #     register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"
    #     response = requests.post(register_url, json=test_user, headers=HEADERS)
    #     response_data = response.json()
    #     assert response.status_code == 201, "Ошибка регистрации пользователя"
    #     assert response_data["email"] == test_user["email"], "Email не совпадает"
    #     assert "id" in response_data, "ID пользователя отсутствует в ответе"
    #     assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
    #     assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"        

    # def test_login_temp_user(self, test_user_login_data):
    #     response = requests.post(f"{BASE_URL}{LOGIN_ENDPOINT}", json=test_user_login_data, headers=HEADERS)
    #     assert response.status_code == 200, "Expected 200: Error at test_login_temp_user"

    # def test_register_session_user(self, session_user): # ! TESTING REGISTRATION
    #     register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"
    #     response = requests.post(register_url, json=session_user, headers=HEADERS)
    #     response_data = response.json()
    #     assert response.status_code == 201, "Ошибка регистрации пользователя"
    #     assert response_data["email"] == session_user["email"], "Email не совпадает"
    #     assert "id" in response_data, "ID пользователя отсутствует в ответе"
    #     assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
    #     assert "USER" in response_data["roles"], "Роль ADMIN должна быть у session пользователя"

    # def test_login_session_user(self, session_user): # ! TESTING LOGIN + TEARDOWN
    #     login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
    #     login_data = {
    #     "email": session_user["email"],
    #     "password": session_user["password"]
    #     }
    #     response = requests.post(login_url, json=login_data, headers=HEADERS)
    #     assert response.status_code == 200, "Auth error"

    # def test_patch_user(get_user_id):
    #     url = f"{BASE_URL}/user/{get_user_id}"
    #     response = requests.patch(url)
    #     assert response.status_code == 200, "Expected 200"

    # def test_logout(self, auth_session): # ! TESTING LOGOUT
    #     logout_url = f"{BASE_URL}{LOGOUT_ENDPOINT}"
    #     response = auth_session.get(logout_url)
    #     assert response.status_code == 200, f"Expected 200 but got: {response.status_code}"