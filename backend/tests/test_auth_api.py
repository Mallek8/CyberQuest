def test_register_login_and_me(client):
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": "Ada@Example.com",
            "username": "Ada",
            "display_name": "  Ada   Lovelace  ",
            "password": "Hunt3rpass1",
        },
    )
    assert registered.status_code == 201
    body = registered.json()
    assert body["user"]["email"] == "ada@example.com"
    assert body["user"]["username"] == "ada"
    assert body["user"]["display_name"] == "Ada Lovelace"
    assert body["user"]["level"] == 1

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["username"] == "ada"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "ada@example.com", "password": "Hunt3rpass1"},
    )
    assert login.status_code == 200


def test_duplicate_account_is_rejected(client):
    payload = {
        "email": "ada@example.com",
        "username": "ada",
        "display_name": "Ada Lovelace",
        "password": "Hunt3rpass1",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    duplicate_email = client.post(
        "/api/v1/auth/register",
        json={**payload, "username": "ada2"},
    )
    assert duplicate_email.status_code == 409
    assert duplicate_email.json()["error"]["code"] == "conflict"
    duplicate_username = client.post(
        "/api/v1/auth/register",
        json={**payload, "email": "other@example.com"},
    )
    assert duplicate_username.status_code == 409


def test_login_errors_do_not_reveal_which_field_was_wrong(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "ada@example.com",
            "username": "ada",
            "display_name": "Ada Lovelace",
            "password": "Hunt3rpass1",
        },
    )
    bad_password = client.post(
        "/api/v1/auth/login",
        json={"email": "ada@example.com", "password": "' OR '1'='1"},
    )
    unknown = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "Hunt3rpass1"},
    )
    assert bad_password.status_code == 401
    assert unknown.status_code == 401
    assert bad_password.json()["error"]["message"] == unknown.json()["error"]["message"]


def test_weak_password_and_missing_token(client):
    weak = client.post(
        "/api/v1/auth/register",
        json={
            "email": "ada@example.com",
            "username": "ada",
            "display_name": "Ada",
            "password": "password",
        },
    )
    assert weak.status_code == 422
    assert weak.json()["error"]["code"] == "validation_error"
    assert client.get("/api/v1/auth/me").status_code == 401


def test_login_rate_limit(client):
    for _ in range(10):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "ada@example.com", "password": "Hunt3rpass1"},
        )
        assert response.status_code == 401
    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": "ada@example.com", "password": "Hunt3rpass1"},
    )
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "rate_limited"
