import requests, pytest

def setup_wiremock_mock():
    url = "http://localhost:8080/__admin/mappings"
    payload = {
        "request": {
            "method": "GET",
            "url": "/gismeteo/get/weather" #мы указываем что если ктото сделает запрос на ручку
										                     #http://localhost:8080/gismeteo/get/weather
        },
        "response": {
            "status": 200,# ему вернется ответ с кодом 200
            "body": '{"temperature": 25}',
            "headers": {
                "Content-Type": "application/json"
            }
        }
    }
    response = requests.post(url, json=payload) #Отправляем запрос на наш WireMock

@pytest.mark.smoke_mock
def test_wiremock_instance():
    setup_wiremock_mock()
    response = requests.get("http://localhost:8080/gismeteo/get/weather")
    assert response.status_code == 200
    assert response.json() == {"temperature": 25}
    print("Test passed!")