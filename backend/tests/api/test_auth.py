"""Test authentication API endpoints."""
import pytest
from httpx import AsyncClient


async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


async def test_admin_login(client: AsyncClient, db):
    """Test admin login."""
    # First, create an admin user in the database
    from app.models.user import User
    from app.core.security import get_password_hash

    admin_user = User(
        emp_id="admin001",
        is_admin=True,
        password_hash=get_password_hash("admin123")
    )
    db.add(admin_user)
    await db.commit()

    # Now test login
    response = await client.post(
        "/api/v1/auth/login/admin",
        json={"emp_id": "admin001", "password": "admin123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "Login successful"
    assert "data" in data
    assert "access_token" in data["data"]
    assert "user" in data["data"]
    assert data["data"]["user"]["emp_id"] == "admin001"
    assert data["data"]["user"]["is_admin"] is True


async def test_admin_login_wrong_password(client: AsyncClient, db):
    """Test admin login with wrong password."""
    from app.models.user import User
    from app.core.security import get_password_hash

    admin_user = User(
        emp_id="admin002",
        is_admin=True,
        password_hash=get_password_hash("correct_password")
    )
    db.add(admin_user)
    await db.commit()

    response = await client.post(
        "/api/v1/auth/login/admin",
        json={"emp_id": "admin002", "password": "wrong_password"}
    )

    assert response.status_code == 401


async def test_admin_login_non_admin(client: AsyncClient, db):
    """Test admin login with non-admin user."""
    from app.models.user import User
    from app.core.security import get_password_hash

    regular_user = User(
        emp_id="user001",
        is_admin=False,
        password_hash=get_password_hash("password123")
    )
    db.add(regular_user)
    await db.commit()

    response = await client.post(
        "/api/v1/auth/login/admin",
        json={"emp_id": "user001", "password": "password123"}
    )

    assert response.status_code == 401


async def test_user_login(client: AsyncClient, db):
    """Test regular user login."""
    from app.models.user import User

    user = User(
        emp_id="user001",
        is_admin=False,
        password_hash=None  # Regular users don't have password
    )
    db.add(user)
    await db.commit()

    response = await client.post(
        "/api/v1/auth/login/user",
        json={"emp_id": "user001"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "access_token" in data["data"]


async def test_user_login_nonexistent(client: AsyncClient):
    """Test user login with non-existent employee ID."""
    response = await client.post(
        "/api/v1/auth/login/user",
        json={"emp_id": "nonexistent"}
    )

    assert response.status_code == 401


async def test_protected_endpoint_without_token(client: AsyncClient):
    """Test accessing protected endpoint without token."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_protected_endpoint_with_invalid_token(client: AsyncClient):
    """Test accessing protected endpoint with invalid token."""
    client.headers.update({"Authorization": "Bearer invalid_token"})
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_get_current_user_info(auth_client: AsyncClient):
    """Test getting current user info."""
    response = await auth_client.get("/api/v1/auth/me")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data
    assert data["data"]["emp_id"] == "admin001"


async def test_logout(auth_client: AsyncClient):
    """Test logout."""
    response = await auth_client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "Logout successful"
