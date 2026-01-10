# Quickstart Guide: Todo Web Application

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
   - `BETTER_AUTH_SECRET`: A random secret string for JWT signing
   - `BETTER_AUTH_URL`: Your application's base URL

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the backend server:
   ```bash
   uvicorn src.main:app --reload
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

4. Start the development server:
   ```bash
   npm run dev
   ```

## Running the Application

1. Start the backend server (port 8000 by default)
2. Start the frontend server (port 3000 by default)
3. Open your browser to `http://localhost:3000`
4. Register a new account or log in to existing account
5. Create, view, update, and manage your tasks

## API Endpoints

Once running, the backend API will be available at:
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login existing user
- `GET /api/{user_id}/tasks` - Get user's tasks
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks/{id}` - Get specific task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Configuration

### Environment Variables

**Backend (.env):**
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Secret key for JWT signing
- `BETTER_AUTH_URL`: Application base URL
- `ENVIRONMENT`: Environment (development/production)

**Frontend (.env.local):**
- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Better Auth base URL