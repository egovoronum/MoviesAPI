import requests, pytest, allure

@allure.title("Проверяем поднят ли Wiremock")
@allure.step("Поднимаем Wiremock и загружаем маппинг")
@pytest.mark.smoke_mock
@pytest.mark.skip
def test_wiremock_instance():
    setup_wiremock_mock()

    with allure.step("Запрашиваем погоду у Wiremock"):
        response = requests.get("http://localhost:8080/gismeteo/get/weather")

    with allure.step("Проверяем статус код ответа"):
        assert response.status_code == 200

    with allure.step("Проверяем тело ответа"):
        assert response.json() == {"temperature": 25}

    print("Test passed!")


def setup_wiremock_mock():
    with allure.step("Определяем URL админки Wiremock"):
        url = "http://localhost:8080/__admin/mappings"

    with allure.step("Подготавливаем маппинг для /gismeteo/get/weather"):
        payload = {
            "request": {
                "method": "GET",
                "url": "/gismeteo/get/weather"
            },
            "response": {
                "status": 200,
                "body": '{"temperature": 25}',
                "headers": {
                    "Content-Type": "application/json"
                }
            }
        }

    with allure.step("Загружаем маппинг в Wiremock"):
        requests.post(url, json=payload)

