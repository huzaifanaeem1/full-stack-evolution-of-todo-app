# API Contract: Frontend Completion & Secure API Integration

## Authentication API

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

#### Response 401 Unauthorized
```json
{
  "detail": "Incorrect email or password"
}
```

### POST /api/auth/register
Register a new user account

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
  "created_at": "2026-01-09T10:00:00Z"
}
```

#### Response 400 Bad Request
```json
{
  "detail": "A user with this email already exists"
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

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### Response 403 Forbidden
```json
{
  "detail": "Access denied - cannot access another user's tasks"
}
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

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### Response 403 Forbidden
```json
{
  "detail": "Access denied - cannot create tasks for another user"
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

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### Response 403 Forbidden
```json
{
  "detail": "Access denied - cannot access another user's tasks"
}
```

#### Response 404 Not Found
```json
{
  "detail": "Task not found"
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

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### Response 403 Forbidden
```json
{
  "detail": "Access denied - cannot update another user's tasks"
}
```

#### Response 404 Not Found
```json
{
  "detail": "Task not found"
}
```

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

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### Response 403 Forbidden
```json
{
  "detail": "Access denied - cannot update another user's tasks"
}
```

#### Response 404 Not Found
```json
{
  "detail": "Task not found"
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

#### Response 200 OK
```json
{
  "message": "Task deleted successfully"
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
  "detail": "Access denied - cannot delete another user's tasks"
}
```

#### Response 404 Not Found
```json
{
  "detail": "Task not found"
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied - cannot access another user's tasks"
}
```

### 404 Not Found
```json
{
  "detail": "Task not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```