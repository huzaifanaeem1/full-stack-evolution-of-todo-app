# API Contract: Todo Web Application

## Authentication API

### POST /api/auth/register
Register a new user account

#### Request
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

#### Response 201 Created
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "created_at": "2026-01-09T10:00:00Z"
}
```

#### Response 400 Bad Request
```json
{
  "error": "Invalid input",
  "details": "Email format invalid or password too weak"
}
```

### POST /api/auth/login
Login to existing account

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

### GET /api/auth/me
Get current user info (requires valid JWT)

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Response 200 OK
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "created_at": "2026-01-09T10:00:00Z"
}
```

## Task API

### GET /api/{user_id}/tasks
Get all tasks for a specific user

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user whose tasks to retrieve

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

### POST /api/{user_id}/tasks
Create a new task for a specific user

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user to create the task for

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

### GET /api/{user_id}/tasks/{id}
Get a specific task by ID

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user who owns the task
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

### PUT /api/{user_id}/tasks/{id}
Update a specific task

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user who owns the task
- id: The ID of the task to update

#### Request
```json
{
  "title": "Buy groceries (urgent)",
  "description": "Milk, bread, eggs - needed today",
  "is_completed": false
}
```

#### Response 200 OK
```json
{
  "id": "task-uuid",
  "title": "Buy groceries (urgent)",
  "description": "Milk, bread, eggs - needed today",
  "is_completed": false,
  "user_id": "user-uuid",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T11:00:00Z"
}
```

### DELETE /api/{user_id}/tasks/{id}
Delete a specific task

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user who owns the task
- id: The ID of the task to delete

#### Response 204 No Content

### PATCH /api/{user_id}/tasks/{id}/complete
Toggle completion status of a specific task

#### Headers
```
Authorization: Bearer {jwt-token}
```

#### Path Parameters
- user_id: The ID of the user who owns the task
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
  "updated_at": "2026-01-09T12:00:00Z"
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Valid authentication token required"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Access denied - insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Requested resource does not exist"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```