import requests

BASE_URL = "http://localhost:8080"


# GET / - текущее время во временной зоне сервера
def test_get_current_time_server_timezone():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "<h1>Current Time in ASIA/TOMSK</h1>" in response.text


# GET /<tz_name> - текущее время в указанной временной зоне
def test_get_current_time_specific_timezone():
    tz_name = "Europe/Moscow"
    response = requests.get(f"{BASE_URL}/{tz_name}")
    assert response.status_code == 200
    assert f"<h1>Current Time in {tz_name}</h1>" in response.text


def test_get_current_time_specific_invalid_timezone():
    invalid_tz_name = "INVALID"
    response = requests.get(f"{BASE_URL}/{invalid_tz_name}")
    assert response.status_code == 400


# POST /api/v1/time - текущее время в заданной зоне (если tz не задан, то зона сервера)
def test_post_current_time_timezone():
    payload = {"tz": "Europe/London"}
    response = requests.post(f"{BASE_URL}/api/v1/time", json=payload)
    assert response.status_code == 200
    response_data = response.json()
    assert "current_time" in response_data
    assert "timezone" in response_data
    assert response_data["timezone"] == "Europe/London"

    # Без указания tz
    payload = {}
    response = requests.post(f"{BASE_URL}/api/v1/time", json=payload)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["timezone"] == "ASIA/TOMSK"


# POST /api/v1/date - текущая дата в указанной временной зоне
def test_post_current_date_timezone():
    payload = {"tz": "America/New_York"}
    response = requests.post(f"{BASE_URL}/api/v1/date", json=payload)
    assert response.status_code == 200
    response_data = response.json()
    assert "current_date" in response_data
    assert "timezone" in response_data
    assert response_data["timezone"] == "America/New_York"

    # Без указания tz
    payload = {}
    response = requests.post(f"{BASE_URL}/api/v1/date", json=payload)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["timezone"] == "ASIA/TOMSK"


# POST /api/v1/datediff - разница между датами
def test_post_date_diff():
    start_data = {
        "date": "12.20.2021 22:21:05",
        "tz": "Europe/Moscow"
    }
    end_data = {
        "date": "12.22.2021 22:21:05",
        "tz": "Europe/Moscow"
    }
    payload = {"start": start_data, "end": end_data}
    response = requests.post(f"{BASE_URL}/api/v1/datediff", json=payload)
    assert response.status_code == 200
    response_data = response.json()
    assert "diff" in response_data
    assert response_data["diff"] == 172800.0

    # Если tz не задан
    start_data = {
        "date": "12.20.2021 22:21:05"
    }
    end_data = {
        "date": "12.22.2021 22:21:05"
    }
    payload = {"start": start_data, "end": end_data}
    response = requests.post(f"{BASE_URL}/api/v1/datediff", json=payload)
    assert response.status_code == 200
    response_data = response.json()
    assert "diff" in response_data
    assert response_data["diff"] == 172800.0


if __name__ == "__main__":
    test_get_current_time_server_timezone()
    test_get_current_time_specific_invalid_timezone()
    test_get_current_time_specific_timezone()
    test_post_current_time_timezone()
    test_post_current_date_timezone()
    test_post_date_diff()

    print("Все тесты прошли успешно!")
