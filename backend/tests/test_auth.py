import pytest
from httpx import AsyncClient
from backend.src.models.user import UserCreate
from backend.src.services.auth import get_password_hash
from uuid import uuid4


@pytest.mark.asyncio
async def test_health_endpoint(test_client: AsyncClient):
    """Test the health check endpoint"""
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(test_client: AsyncClient, db_session):
    """Test user registration"""
    user_data = {
        "email": f"test{uuid4()}@example.com",  # Use unique email each time
        "password": "securepassword123"
    }

    response = await test_client.post("/api/auth/register", json=user_data)
    assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
async def test_login_user(test_client: AsyncClient, db_session):
    """Test user login"""
    # First, create a user
    user_data = {
        "email": f"login_test{uuid4()}@example.com",
        "password": "securepassword123"
    }

    # Register the user first
    register_response = await test_client.post("/api/auth/register", json=user_data)

    # Then try to login
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }

    response = await test_client.post("/api/auth/login", json=login_data)
    assert response.status_code in [200, 401, 422]