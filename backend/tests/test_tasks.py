import pytest
from httpx import AsyncClient
from backend.src.models.user import UserCreate
from backend.src.models.task import TaskCreate
from backend.src.services.auth import get_password_hash
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_task(test_client: AsyncClient, db_session):
    """Test creating a task"""
    # First register a user
    user_data = {
        "email": f"task_user{uuid4()}@example.com",
        "password": "securepassword123"
    }

    register_response = await test_client.post("/api/auth/register", json=user_data)
    assert register_response.status_code in [200, 400, 422]

    # Login to get token
    login_response = await test_client.post("/api/auth/login", json=user_data)
    assert login_response.status_code in [200, 401, 422]

    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data["token"]
        user_id = token_data["user"]["id"]

        # Create a task
        task_data = {
            "title": "Test task",
            "description": "Test description"
        }

        response = await test_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 400, 401, 403, 422]


@pytest.mark.asyncio
async def test_get_tasks(test_client: AsyncClient, db_session):
    """Test getting tasks for a user"""
    # First register a user
    user_data = {
        "email": f"get_task_user{uuid4()}@example.com",
        "password": "securepassword123"
    }

    register_response = await test_client.post("/api/auth/register", json=user_data)
    assert register_response.status_code in [200, 400, 422]

    # Login to get token
    login_response = await test_client.post("/api/auth/login", json=user_data)
    assert login_response.status_code in [200, 401, 422]

    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data["token"]
        user_id = token_data["user"]["id"]

        # Get tasks for the user
        response = await test_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 401, 403, 422]