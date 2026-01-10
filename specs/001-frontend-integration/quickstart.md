# Quickstart Guide: Frontend Completion & Secure API Integration

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

## Frontend Pages

### Login Page (`/login`)
- Accessible at `/login`
- Contains email and password fields
- Handles user authentication
- Redirects to `/tasks` after successful login

### Register Page (`/register`)
- Accessible at `/register`
- Contains email and password fields
- Handles new user registration
- Redirects to `/login` after successful registration

### Tasks Page (`/tasks`)
- Accessible at `/tasks` (requires authentication)
- Displays user's tasks in a list
- Provides create, update, and delete functionality
- Shows visual distinction between completed and pending tasks

## API Integration

### JWT Token Handling
- Tokens are obtained during login/registration
- Tokens are attached to all authenticated API requests
- Tokens are stored securely in the browser
- Automatic logout on token expiration

### Frontend State Management
- Tasks are managed with React state
- UI updates immediately after successful API calls
- Loading states displayed during API requests
- Error states displayed for failed requests

## Security Features

### Authentication
- JWT-based authentication on all API endpoints
- User ID verification in URL parameters
- 401 responses for invalid tokens
- 403 responses for cross-user access attempts

### Data Isolation
- Users can only access their own tasks
- Backend validates user ownership on all operations
- Frontend only displays user's own tasks

## Testing

### Manual Testing Steps

1. **Authentication Flow**
   - Register a new user account
   - Log in with valid credentials
   - Verify access to tasks page

2. **Task Management**
   - Create a new task
   - Verify task appears in list immediately
   - Update task completion status
   - Delete a task
   - Verify all operations work without page refresh

3. **Security Verification**
   - Attempt to access tasks without authentication (should redirect to login)
   - Verify that tasks are isolated between different users
   - Verify unauthorized access returns appropriate error codes

## Environment Variables

### Frontend (.env.local)
- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL

### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Secret key for JWT signing
- `BETTER_AUTH_URL`: Application base URL
- `ENVIRONMENT`: Environment (development/production)