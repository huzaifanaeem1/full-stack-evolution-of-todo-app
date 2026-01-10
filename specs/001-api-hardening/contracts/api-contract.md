# API Contract: Secure Todo API with JWT Authentication

## Authentication Endpoints

### POST /api/auth/register
Register a new user account with JWT-based authentication

#### Request
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

#### Response 200 OK
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T10:00:00Z"
}
```

#### Response 400 Bad Request
```json
{
  "detail": "A user with this email already exists"
}
```

### POST /api/auth/login
Authenticate user and return JWT token

#### Request
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

#### Response 200 OK
```json
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com"
  },
  "token": "jwt-token-string"
}
```

#### Response 401 Unauthorized
```json
{
  "detail": "Incorrect email or password"
}
```

### GET /api/auth/me
Get current authenticated user info (requires JWT)

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Response 200 OK
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T10:00:00Z"
}
```

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

## Task Management Endpoints

### GET /api/{user_id}/tasks
Get all tasks for a specific user (requires valid JWT matching user_id)

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user whose tasks to retrieve (must match JWT user ID)

#### Response 200 OK
```json
[
  {
    "id": "task-uuid",
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "is_completed": false,
    "user_id": "user-uuid",
    "created_at": "2026-01-09T10:00:00Z",
    "updated_at": "2026-01-09T10:00:00Z"
  }
]
```

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### Response 403 Forbidden
```json
{
  "detail": "Access denied - user_id in URL does not match authenticated user"
}
```

### POST /api/{user_id}/tasks
Create a new task for a specific user (requires valid JWT matching user_id)

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user to create the task for (must match JWT user ID)

#### Request
```json
{
  "title": "Buy groceries",
  "description": "Milk, bread, eggs"
}
```

#### Response 201 Created
```json
{
  "id": "task-uuid",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "is_completed": false,
  "user_id": "user-uuid",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T10:00:00Z"
}
```

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### Response 403 Forbidden
```json
{
  "detail": "Access denied - user_id in URL does not match authenticated user"
}
```

### GET /api/{user_id}/tasks/{id}
Get a specific task by ID for a specific user (requires valid JWT matching user_id)

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user who owns the task (must match JWT user ID)
- id: The ID of the task to retrieve

#### Response 200 OK
```json
{
  "id": "task-uuid",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "is_completed": false,
  "user_id": "user-uuid",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T10:00:00Z"
}
```

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### Response 403 Forbidden
```json
{
  "detail": "Access denied - user_id in URL does not match authenticated user"
}
```

#### Response 404 Not Found
```json
{
  "detail": "Task not found"
}
```

### PUT /api/{user_id}/tasks/{id}
Update a specific task for a specific user (requires valid JWT matching user_id)

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user who owns the task (must match JWT user ID)
- id: The ID of the task to update

#### Request
```json
{
  "title": "Buy groceries (urgent)",
  "description": "Milk, bread, eggs - needed today",
  "is_completed": true
}
```

#### Response 200 OK
```json
{
  "id": "task-uuid",
  "title": "Buy groceries (urgent)",
  "description": "Milk, bread, eggs - needed today",
  "is_completed": true,
  "user_id": "user-uuid",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T11:00:00Z"
}
```

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### Response 403 Forbidden
```json
{
  "detail": "Access denied - user_id in URL does not match authenticated user"
}
```

#### Response 404 Not Found
```json
{
  "detail": "Task not found"
}
```

### PATCH /api/{user_id}/tasks/{id}
Partially update a specific task for a specific user (requires valid JWT matching user_id)

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user who owns the task (must match JWT user ID)
- id: The ID of the task to update

#### Request
```json
{
  "is_completed": true
}
```

#### Response 200 OK
```json
{
  "id": "task-uuid",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "is_completed": true,
  "user_id": "user-uuid",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T11:00:00Z"
}
```

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### Response 403 Forbidden
```json
{
  "detail": "Access denied - user_id in URL does not match authenticated user"
}
```

#### Response 404 Not Found
```json
{
  "detail": "Task not found"
}
```

### DELETE /api/{user_id}/tasks/{id}
Delete a specific task for a specific user (requires valid JWT matching user_id)

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user who owns the task (must match JWT user ID)
- id: The ID of the task to delete

#### Response 204 No Content

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### Response 403 Forbidden
```json
{
  "detail": "Access denied - user_id in URL does not match authenticated user"
}
```

#### Response 404 Not Found
```json
{
  "detail": "Task not found"
}
```

## Security Requirements

### JWT Token Validation
- All protected endpoints require valid JWT in Authorization header
- Token must be properly formatted with correct signature
- Token must not be expired
- User ID in token must match user ID in URL path for user-specific operations

### User Data Isolation
- Users can only access their own tasks
- Backend enforces user_id matching between JWT and URL parameters
- Cross-user access attempts return 403 Forbidden status

### Error Responses
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: User attempting to access another user's data
- 404 Not Found: Requested resource does not exist
- Proper error messages that don't expose sensitive information