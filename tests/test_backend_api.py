"""Funções pytest tipadas verificam contratos HTTP, isolamento e agregações."""

from fastapi.testclient import TestClient

from app.services.engine import count_by_severity


def register(client: TestClient, email: str) -> None:
    """Cria usuário de teste usando a interface pública de registro."""

    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correct-horse-battery"},
    )
    assert response.status_code == 201


def login(client: TestClient, email: str) -> str:
    """Obtém access token usando o formulário OAuth2 password."""

    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "correct-horse-battery"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_analytics_events_are_authenticated_and_scoped_to_user(client: TestClient) -> None:
    """Garante autenticação obrigatória e que usuários não leem eventos alheios."""

    unauthenticated = client.get("/api/v1/analytics/events")
    assert unauthenticated.status_code == 401

    register(client, "first@example.com")
    first_token = login(client, "first@example.com")
    first_headers = {"Authorization": f"Bearer {first_token}"}

    created = client.post(
        "/api/v1/analytics/events",
        json={"severity": "ERROR", "message": "database timeout"},
        headers=first_headers,
    )
    assert created.status_code == 201
    assert created.json()["severity"] == "ERROR"

    register(client, "second@example.com")
    second_headers = {"Authorization": f"Bearer {login(client, 'second@example.com')}"}
    assert client.get("/api/v1/analytics/events", headers=second_headers).json() == []

    summary = client.get("/api/v1/analytics/summary", headers=first_headers)
    assert summary.status_code == 200
    assert summary.json() == {
        "total_events": 1,
        "by_severity": [{"severity": "ERROR", "count": 1}],
    }


def test_registration_rejects_duplicate_email_and_short_password(client: TestClient) -> None:
    """Valida restrições de senha e conflito de email na borda HTTP."""

    register(client, "duplicate@example.com")
    duplicate = client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "correct-horse-battery"},
    )
    assert duplicate.status_code == 409

    invalid_password = client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "short"},
    )
    assert invalid_password.status_code == 422


def test_count_by_severity_aggregates_without_losing_repeated_values() -> None:
    """Confirma o contrato da função pura que agrega severidades."""

    assert count_by_severity(["ERROR", "INFO", "ERROR"]) == {"ERROR": 2, "INFO": 1}
