# Quickstart Guide: API Hardening and Validation

## Prerequisites

- Node.js 18+ for frontend development
- Python 3.11+ for backend development
- PostgreSQL (or access to Neon Serverless PostgreSQL)
- Git

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying the example file:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `BETTER_AUTH_SECRET`: A random secret string for JWT signing (make it very long and random)
   - `BETTER_AUTH_URL`: Your application's base URL (e.g., http://localhost:3000)

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the backend server:
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables by copying the example file:
   ```bash
   cp .env.local.example .env.local
   ```

   Edit `.env.local` and set:
   - `NEXT_PUBLIC_API_BASE_URL`: Base URL of your backend API (e.g., http://localhost:8000)
   - `NEXT_PUBLIC_BETTER_AUTH_URL`: Better Auth base URL (e.g., http://localhost:3000)

4. Start the development server:
   ```bash
   npm run dev
   ```

## API Security Features

### JWT Authentication
- All API endpoints require a valid JWT token in the Authorization header
- Format: `Authorization: Bearer <token>`
- Tokens are issued during login and registration
- Tokens expire after 30 minutes (configurable via ACCESS_TOKEN_EXPIRE_MINUTES)

### User Data Isolation
- Users can only access their own tasks
- Backend validates that user_id in URL matches the user_id in the JWT token
- Attempts to access another user's data return 403 Forbidden

### Error Handling
- 401 Unauthorized: Missing or invalid JWT token
- 403 Forbidden: Attempting to access another user's data
- 404 Not Found: Resource doesn't exist
- Descriptive error messages for debugging

## Testing the API

### Authentication Flow
1. Register a new user: `POST /api/auth/register`
2. Login to get a JWT: `POST /api/auth/login`
3. Use the JWT to access protected endpoints

### Task Management
1. Create tasks: `POST /api/{user_id}/tasks`
2. List tasks: `GET /api/{user_id}/tasks`
3. Update tasks: `PUT /api/{user_id}/tasks/{id}`
4. Delete tasks: `DELETE /api/{user_id}/tasks/{id}`

### Security Testing
- Try accessing endpoints without a JWT (should return 401)
- Try accessing another user's tasks with your JWT (should return 403)
- Try using an expired or invalid JWT (should return 401)

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Secret key for JWT signing
- `BETTER_AUTH_URL`: Application base URL
- `ENVIRONMENT`: Environment (development/production)

### Frontend (.env.local)
- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Better Auth base URL