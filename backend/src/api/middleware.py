from fastapi import HTTPException, status, Request
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import os
from ..models.user import User
from ..config.database import get_db_session as get_async_db_session
from sqlmodel import select
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

# JWT configuration
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError("BETTER_AUTH_SECRET environment variable must be set for security")
ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)  # auto_error=False allows us to handle it ourselves


async def verify_jwt_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return user ID if valid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        return user_id

    except JWTError:
        raise credentials_exception


async def get_current_user_from_token(token: str, db) -> User:
    """
    Get current user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = await verify_jwt_token(token)

    statement = select(User).where(User.id == user_id)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def jwt_required(request: Request, call_next):
    """
    Middleware to verify JWT token on all requests (except public endpoints)
    """
    # Define public endpoints that don't require authentication
    public_endpoints = ["/", "/health", "/docs", "/redoc", "/openapi.json"]

    # Skip authentication for public endpoints
    if request.url.path in public_endpoints or request.url.path.startswith("/static/"):
        response = await call_next(request)
        return response

    # For all other endpoints, require authentication
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid format"
        )

    token = auth_header.split(" ")[1]  # Extract token from "Bearer <token>"

    # Verify the token
    try:
        user_id = await verify_jwt_token(token)

        # Add user ID to request state for use in endpoints
        request.state.user_id = user_id

        # Continue with the request
        response = await call_next(request)
        return response
    except HTTPException:
        # Re-raise HTTP exceptions (like 401)
        raise
    except Exception:
        # For any other error during token verification
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def validate_user_ownership(request: Request, call_next):
    """
    Middleware to validate that the user_id in the URL matches the authenticated user
    This is specifically for endpoints that have a user_id in the path like /api/{user_id}/tasks
    """
    # Get the URL path and check if it contains a user_id parameter
    path = request.url.path

    # Check if the path pattern matches endpoints with user_id in the URL
    # For example: /api/some-uuid-here/tasks, /api/some-uuid-here/tasks/task-id
    import re
    user_id_match = re.search(r'/api/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/', path)

    if user_id_match:
        url_user_id = user_id_match.group(1)
        authenticated_user_id = getattr(request.state, 'user_id', None)

        # If there's no authenticated user, the jwt_required middleware should have caught this
        if not authenticated_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        # Check if the user_id in the URL matches the authenticated user
        if url_user_id != authenticated_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied - cannot access another user's resources"
            )

    # Continue with the request
    response = await call_next(request)
    return response