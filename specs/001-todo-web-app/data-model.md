# Data Model: Todo Web Application

## Entity: User

### Fields
- **id** (UUID/Integer): Primary key, unique identifier for the user
- **email** (String): User's email address, must be unique
- **password_hash** (String): Hashed password using secure hashing algorithm
- **created_at** (DateTime): Timestamp when the user account was created
- **updated_at** (DateTime): Timestamp when the user account was last updated
- **is_active** (Boolean): Flag indicating if the user account is active

### Relationships
- **tasks**: One-to-many relationship with Task entity (one user can have many tasks)

### Validation Rules
- Email must be valid format and unique across all users
- Password must meet minimum strength requirements (handled by auth library)
- Email and password are required for registration

## Entity: Task

### Fields
- **id** (UUID/Integer): Primary key, unique identifier for the task
- **title** (String): Title of the task (required)
- **description** (String): Optional description of the task
- **is_completed** (Boolean): Flag indicating if the task is completed (default: False)
- **user_id** (UUID/Integer): Foreign key linking to the User who owns this task
- **created_at** (DateTime): Timestamp when the task was created
- **updated_at** (DateTime): Timestamp when the task was last updated

### Relationships
- **user**: Many-to-one relationship with User entity (many tasks belong to one user)

### Validation Rules
- Title is required and must not be empty
- Description is optional and can be null
- User ID is required and must reference an existing user
- Task can only be modified by the owning user

## State Transitions

### Task State Transitions
- **Incomplete → Complete**: When user marks task as complete via PATCH /api/{user_id}/tasks/{id}/complete
- **Complete → Incomplete**: When user unmarks task as complete via PATCH /api/{user_id}/tasks/{id}/complete

## Constraints

### Data Integrity
- Foreign key constraint: Task.user_id must reference an existing User.id
- Not null constraints: Task.title and Task.user_id cannot be null
- Unique constraint: User.email must be unique

### Business Logic
- Users can only access/modify their own tasks
- Tasks cannot be transferred between users
- Completed tasks remain accessible for historical purposes