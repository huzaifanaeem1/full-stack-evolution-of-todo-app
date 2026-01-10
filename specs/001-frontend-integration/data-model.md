# Data Model: Frontend Completion & Secure API Integration

## Entity: User Session

### Fields
- **token** (String): JWT token for authenticated requests
- **userId** (UUID/String): Unique identifier of the authenticated user
- **expiresAt** (DateTime): Expiration time of the JWT token
- **userData** (Object): Additional user information retrieved from the backend

### State Transitions
- **Unauthenticated → Authenticating**: When user submits login/registration form
- **Authenticating → Authenticated**: When backend returns valid JWT token
- **Authenticated → Unauthenticated**: When user logs out or token expires

## Entity: Task List

### Fields
- **tasks** (Array): Collection of task objects belonging to the authenticated user
- **isLoading** (Boolean): Flag indicating if tasks are being loaded from the backend
- **hasError** (Boolean): Flag indicating if there was an error loading tasks
- **error** (String): Error message if there was a problem with operations

### State Transitions
- **Empty → Loading**: When fetching tasks from the backend
- **Loading → Loaded**: When tasks are successfully retrieved
- **Loaded → Updating**: When performing CRUD operations on tasks
- **Updating → Loaded**: When CRUD operation completes successfully

## Frontend State Management

### Session State
- **Purpose**: Track authentication status and user identity across the application
- **Persistence**: Store JWT token in browser's secure storage (localStorage/cookies)
- **Validation**: Verify token validity before making API requests

### Task State
- **Purpose**: Maintain local copy of user's tasks for immediate UI updates
- **Sync Strategy**: Update local state optimistically after API requests
- **Conflict Resolution**: Refresh from backend on error or periodically

## API Interaction Patterns

### Request Flow
1. Check authentication status
2. Attach JWT token to Authorization header
3. Send request to backend API
4. Handle response and update UI state

### Response Handling
- **Success**: Update local state, reflect changes in UI
- **401 Error**: Redirect to login, clear session state
- **403 Error**: Show error message, maintain current state
- **Network Error**: Show error state, allow retry

## Validation Rules

### Frontend Validation
- JWT token presence before authenticated API calls
- Form input validation before submission
- Response format validation from backend

### Backend Validation
- JWT token validity and signature verification
- User ID matching between token and URL parameter
- Authorization checks for cross-user access prevention

## Security Constraints

### Token Security
- JWT tokens stored securely in frontend
- Automatic token refresh when approaching expiration
- Proper cleanup on logout or session termination

### Data Isolation
- Backend enforces user ID matching for all operations
- Frontend only displays tasks belonging to authenticated user
- API calls include user-specific identifiers for validation