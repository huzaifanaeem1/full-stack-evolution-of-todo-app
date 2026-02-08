# Evolution of Todo: Full-Stack Web Application

## Overview

This repository contains the implementation of a multi-user todo web application with secure authentication, task management, and proper user data isolation. The application consists of a Next.js frontend with App Router and a FastAPI backend with JWT-based authentication.

This project was built using **Spec-Driven Development (SDD)** methodology, progressing through multiple phases from specification to implementation.

## Development Phases

### Phase 2 - Part 1: Backend Foundation & Authentication (001-todo-web-app)
**Objective**: Transform the CLI todo app into a modern multi-user web application with persistent storage.

**What Was Built**:
- ✅ FastAPI backend with REST API architecture
- ✅ SQLModel ORM integration with Neon Serverless PostgreSQL
- ✅ JWT-based authentication system using Better Auth
- ✅ User registration and login functionality
- ✅ Complete CRUD operations for tasks (Create, Read, Update, Delete)
- ✅ Task completion toggle functionality
- ✅ User data isolation - users can only access their own tasks
- ✅ Database schema with User and Task models
- ✅ Environment-based configuration management

**Key Achievements**:
- Implemented secure authentication flow with JWT tokens
- Established proper user-task relationships in the database
- Created RESTful API endpoints following best practices
- Set up database migrations with Alembic
- Configured Neon PostgreSQL for serverless deployment

### Phase 2 - Part 2: Frontend Integration & UI (001-frontend-integration)
**Objective**: Complete the frontend implementation and establish secure API integration between frontend and backend.

**What Was Built**:
- ✅ Next.js 16+ App Router implementation
- ✅ Login page (`/login`) with authentication flow
- ✅ Registration page (`/register`) for new users
- ✅ Tasks dashboard (`/tasks`) for task management
- ✅ Responsive UI design (mobile + desktop)
- ✅ Real-time UI updates without page refresh
- ✅ JWT token management and automatic attachment to API requests
- ✅ Loading, error, and success state handling
- ✅ Axios-based API client with interceptors
- ✅ Visual distinction between completed and pending tasks

**Key Achievements**:
- Seamless frontend-backend communication with JWT authentication
- Immediate UI feedback for all CRUD operations
- Proper error handling and user feedback
- Responsive design that works across devices
- Secure token storage and management

### Phase 2 - Part 3: Security Hardening & Validation (001-api-hardening)
**Objective**: Harden the application security, validate API behavior, and ensure compliance with requirements.

**What Was Built**:
- ✅ Comprehensive JWT validation on ALL API endpoints
- ✅ User ID verification - URL user_id must match JWT user_id
- ✅ Proper HTTP status codes (200, 201, 401, 403, 404)
- ✅ Cross-user access prevention with 403 Forbidden responses
- ✅ Unauthorized request handling with 401 responses
- ✅ Input validation and error handling
- ✅ Security testing and validation
- ✅ Documentation updates with security details

**Key Achievements**:
- 100% of API endpoints require valid JWT authentication
- Zero cross-user data access - complete user isolation
- Proper error responses with appropriate status codes
- No hardcoded secrets - all configuration via environment variables
- Comprehensive security validation and testing

### Phase 4: Kubernetes Deployment with Minikube (003-minikube-deployment)
**Objective**: Deploy the Todo Chatbot application to a local Kubernetes cluster using Minikube with Helm for package management.

**What Was Built**:
- ✅ Docker containerization with multi-stage builds
  - Frontend Dockerfile (Node 20 Alpine, optimized for Next.js 16+)
  - Backend Dockerfile (Python 3.11 slim, optimized for FastAPI)
- ✅ Helm chart structure (`helm/todo-chatbot/`)
  - Chart.yaml with metadata
  - values.yaml with configurable parameters
  - Kubernetes resource templates (Deployments, Services, ConfigMaps, Secrets)
- ✅ Kubernetes deployment configuration
  - Frontend Deployment with health checks and resource limits
  - Backend Deployment with health checks and resource limits
  - NodePort Services for external access
  - ConfigMap for environment configuration
  - Secrets for sensitive data (DATABASE_URL, JWT_SECRET)
- ✅ Service communication validation
  - Frontend accessible via port-forward (HTTP 200)
  - Backend health endpoint responding correctly
  - Inter-service communication via Kubernetes DNS verified

**Key Achievements**:
- Successfully built and loaded Docker images into Minikube
- Deployed application using Helm chart
- All pods running and ready (1/1 Ready state)
- Service-to-service communication working via Kubernetes DNS
- No code modifications to Phase III application
- Production-ready containerization with security best practices

## Project Evolution Summary

This project demonstrates a complete evolution from specification to production-ready application:

1. **Specification Phase**: Detailed requirements and user stories defined
2. **Planning Phase**: Architecture decisions and implementation strategy
3. **Task Breakdown**: Granular, testable tasks created
4. **Implementation Phase**: Systematic development following the plan
5. **Validation Phase**: Security hardening and requirement verification

The result is a secure, scalable, multi-user todo application with proper authentication, authorization, and data isolation.

## Features

- **User Authentication**: Secure registration and login with JWT tokens
- **Task Management**: Create, read, update, and delete personal tasks
- **User Isolation**: Users can only access their own tasks
- **Responsive UI**: Works on desktop and mobile devices
- **Real-time Updates**: Tasks update immediately without page refresh
- **Secure API**: All endpoints require JWT authentication with proper user validation

## Tech Stack

### Backend
- **Framework**: FastAPI
- **ORM**: SQLModel with PostgreSQL
- **Authentication**: JWT-based with custom authentication service
- **Database**: Neon Serverless PostgreSQL

### Frontend
- **Framework**: Next.js 16+ with App Router
- **Styling**: Tailwind CSS
- **API Client**: Axios with automatic JWT attachment
- **State Management**: React hooks

## Architecture

The application follows a microservice architecture with separate frontend and backend services:

```
frontend/ - Next.js application with App Router
├── src/
│   ├── app/          # Pages using App Router
│   ├── components/   # Reusable UI components
│   ├── services/     # API and auth utilities
│   └── types/        # TypeScript type definitions
└── package.json

backend/ - FastAPI application
├── src/
│   ├── models/       # SQLModel database models
│   ├── services/     # Business logic
│   ├── api/          # API route handlers
│   └── config/       # Configuration and database setup
├── requirements.txt
└── alembic/          # Database migrations
```

## Security Features

- **JWT Authentication**: All API endpoints require valid JWT tokens
- **User Isolation**: Users can only access their own data
- **Token Validation**: Automatic token expiration checking
- **Input Validation**: All inputs validated using Pydantic/TypeScript types
- **SQL Injection Protection**: ORM-based queries prevent injection attacks
- **Cross-User Access Prevention**: All endpoints validate that the user_id in the URL matches the authenticated user's ID
- **Proper Error Handling**: Standardized HTTP status codes (401, 403, 404) with clear error messages
- **Secure Token Storage**: JWT tokens stored securely in browser localStorage with proper cleanup

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Authenticate user and return JWT token
- `GET /api/auth/me` - Get current user info

### Tasks (per user)
- `GET /api/{user_id}/tasks` - Get user's tasks (returns 403 if user_id doesn't match authenticated user)
- `POST /api/{user_id}/tasks` - Create new task (returns 403 if user_id doesn't match authenticated user)
- `GET /api/{user_id}/tasks/{id}` - Get specific task (returns 403 if user_id doesn't match authenticated user)
- `PUT /api/{user_id}/tasks/{id}` - Update task (returns 403 if user_id doesn't match authenticated user)
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion (returns 403 if user_id doesn't match authenticated user)
- `DELETE /api/{user_id}/tasks/{id}` - Delete task (returns 403 if user_id doesn't match authenticated user)

All endpoints require JWT authentication and validate that the user_id in the URL matches the authenticated user's ID.

## Security Implementation Details

### Backend Security
- JWT tokens are validated on every protected endpoint using dependency injection
- User ID from JWT payload is compared against user_id in URL path parameter
- All error responses return standardized HTTP status codes (200/201 for success, 401 for unauthorized, 403 for forbidden access, 404 for not found)
- Cross-user access attempts are prevented with 403 Forbidden responses

### Frontend Security
- JWT tokens are automatically attached to all API requests via Axios interceptors
- 401 responses trigger automatic logout and redirect to login page
- 403 responses are logged and handled appropriately
- Token expiration is checked before API calls
- Secure token storage with automatic cleanup on logout/error

## Setup

### Prerequisites

- Node.js 18+ for frontend
- Python 3.11+ for backend
- PostgreSQL (or Neon Serverless PostgreSQL)
- Git

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
   - `BETTER_AUTH_URL`: Your application's base URL
   - `ENVIRONMENT`: Environment (development/production)

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
   - `NEXT_PUBLIC_API_BASE_URL`: Base URL of your backend API (e.g., http://localhost:8000/api)

4. Start the development server:
   ```bash
   npm run dev
   ```

## Development

### Running Tests

Backend tests:
```bash
cd backend
python -m pytest
```

Frontend tests:
```bash
cd frontend
npm run test
```

### Environment Variables

#### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Secret key for JWT signing
- `BETTER_AUTH_URL`: Application base URL
- `ENVIRONMENT`: Environment (development/production)

#### Frontend (.env.local)
- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL

## API Security Validation

The application has been hardened and validated with the following security measures:

1. **JWT Token Verification**: All API endpoints require valid JWT tokens
2. **User ID Validation**: URL parameters are validated against JWT payload
3. **Data Isolation**: Users can only access their own tasks
4. **Proper Error Handling**: Standardized HTTP status codes with appropriate messages
5. **Cross-User Access Prevention**: Attempts to access another user's data result in 403 Forbidden
6. **Secure Configuration**: No hardcoded secrets, all sensitive data via environment variables
7. **Frontend Security**: Proper JWT handling and error response processing

## Manual Test Scenarios

To validate security implementation:

1. **Unauthorized Access**: Attempt API calls without JWT token (should return 401)
2. **Cross-User Access**: Attempt to access another user's tasks (should return 403)
3. **Valid Access**: Authenticate and access own data (should return 200/201)
4. **Invalid Token**: Use expired/invalid token (should return 401)
5. **Token Expiration**: Verify automatic logout on token expiration
6. **Error Messages**: Verify proper error messages without sensitive information

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the excellent web framework
- Next.js for the React framework
- SQLModel for the ORM
- The open-source community for countless tools and libraries that made this project possible.# evolution-of-todo-hackathon
# full-stack-evolution-of-todo-hackathon
