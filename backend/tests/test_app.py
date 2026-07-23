import io
import pytest

def test_register_login_logout(client):
    register = client.post(
        "/register",
        json={"username": "newuser", "password": "secret123", "email": "new@example.com"},
    )
    assert register.status_code == 201
    assert register.get_json()["user"]["username"] == "newuser"

    me_after_register = client.get("/valid-user")
    assert me_after_register.status_code == 200
    assert me_after_register.get_json()["user"]["username"] == "newuser"

    logout = client.post("/logout")
    assert logout.status_code == 200

    login = client.post("/login", json={"username": "newuser", "password": "secret123"})
    assert login.status_code == 200
    assert login.get_json()["user"]["username"] == "newuser"

def test_login_rejects_bad_password(client):
    response = client.post("/login", json={"username": "testuser", "password": "wrong"})
    assert response.status_code == 401

def test_create_report(client, mock_valid_csv_file, mock_no_header_csv_file):
    client.post(
        "/register",
        json={"username": "newuser", "password": "secret123", "email": "new@example.com"},
    )

    client.post("/login", json={"username": "newuser", "password": "secret123"})

    file = mock_valid_csv_file()
    file.stream.seek(0)
    data = {
        "returnType": "JSON",
    }
    data["report"] = (file.stream, file.filename)

    good_response = client.post("/create-report", data=data, content_type="multipart/form-data")

    assert good_response.status_code == 200
    body = good_response.get_json()
    assert body["Status"] == "Success"

    file = mock_no_header_csv_file()
    file.stream.seek(0)
    data = {
        "returnType": "JSON",
    }
    data["report"] = (file.stream, file.filename)

    missing_header_response = client.post("/create-report", data=data, content_type="multipart/form-data")

    assert missing_header_response.status_code == 400

def test_upload_report(client, mock_valid_user):
    client.post(
        "/register",
        json={"username": "newuser", "password": "secret123", "email": "new@example.com"},
    )

    client.post("/login", json={"username": "newuser", "password": "secret123"})

    payload = {
        "transactions": {
            "t1": {
                "group": "purchase",
                "value": 10.0,
                "date": "2024-01-01",
                "info": "t",
                "category": "food_drink",
            }
        },
    }
    response = client.post("/upload-report", json=payload)

    assert response.status_code == 200
    assert response.get_json().get("Status") == "Success"

def test_get_report(client):
    client.post(
        "/register",
        json={"username": "newuser", "password": "secret123", "email": "new@example.com"},
    )

    client.post("/login", json={"username": "newuser", "password": "secret123"})

    oneMonthYear = {
        "date_start": "2026-04",
        "date_end": "2026-04",
        "return_type": "JSON"
    }

    multipleMonthYear = {
        "date_start": "2025-01",
        "date_end": "2026-04",
        "return_type": "JSON"
    }

    missingMonth = {
        "date_end": "2026-04",
        "return_type": "JSON"
    }


    missingYear = {
        "date_start": "2026-04",
        "return_type": "JSON"
    }

    badDate = {
        "date_start": "2026-04",
        "date_end": "2O26-O4",
        "return_type": "JSON"
    }
    
    oneMonthYearResponse = client.post("/get-report", json=oneMonthYear)   
    assert oneMonthYearResponse.status_code == 200

    body = oneMonthYearResponse.get_json()
    assert body["status"] == "success"
    assert "report" in body

    multipleMonthYearResponse = client.post("/get-report", json=multipleMonthYear)   
    assert oneMonthYearResponse.status_code == 200

    body = multipleMonthYearResponse.get_json()
    assert body["status"] == "success"
    assert "report" in body

    missingMonthResponse = client.post("/get-report", json=missingMonth) 
    assert missingMonthResponse.status_code == 400

    missingYearResponse = client.post("/get-report", json=missingYear)
    assert missingYearResponse.status_code == 400

    badDateResponse = client.post("/get-report", json=badDate)
    assert badDateResponse.status_code == 400

def test_get_user_data():
    pass