from fastapi.testclient import TestClient


def register(
    client: TestClient,
    username: str = "ada",
    email: str = "ada@example.com",
) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "display_name": "Ada Lovelace",
            "password": "Hunt3rpass1",
        },
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
