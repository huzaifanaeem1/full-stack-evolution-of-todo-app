# Data Model: API Hardening and Validation

## Entity: JWT Token

### Attributes
- **token** (String): The JWT token string containing user identity and expiration
- **payload** (Object): Decoded JWT claims including user ID and expiration time
- **expiration** (DateTime): Time when the token becomes invalid
- **user_id** (UUID): The authenticated user's unique identifier from the token

### State Transitions
- **Valid → Expired**: When current time exceeds token expiration timestamp
- **Absent → Valid**: When user authenticates successfully and receives new token
- **Valid → Invalid**: When token is tampered with or secret key doesn't match

### Validation Rules
- Token must have valid JWT format (3 parts separated by dots)
- Signature must verify against shared secret key
- Expiration timestamp must be in the future
- User ID must correspond to an existing user in the database

## Entity: API Request

### Attributes
- **method** (String): HTTP method (GET, POST, PUT, PATCH, DELETE)
- **endpoint** (String): API endpoint path with URL parameters
- **headers** (Object): HTTP headers including Authorization
- **authenticated_user** (User): Extracted user identity from JWT (if valid)
- **access_granted** (Boolean): Whether request passes authentication/authorization checks

### State Transitions
- **Unverified → Verified**: When JWT token is successfully decoded and validated
- **Unauthorized → Authorized**: When user ID matches required resource ownership
- **Pending → Processed**: After request is handled and response generated

### Validation Rules
- Authorization header must contain valid JWT token for protected endpoints
- User ID in token must match user ID in URL parameters for user-specific resources
- Request must not access resources belonging to other users

## Entity: Authentication Response

### Attributes
- **status_code** (Integer): HTTP status code (200, 401, 403, etc.)
- **response_body** (Object): Response data or error message
- **error_detail** (String): Specific error information for client handling

### Validation Rules
- Status code must match specification requirements (401 for auth failures, 403 for authorization failures)
- Response body must follow standard format for error cases
- Error messages should be informative but not reveal sensitive information

## Relationships

### JWT Token → User
- One-to-one relationship where JWT token contains user identity information
- Token user_id references User.id for data access validation

### API Request → JWT Token
- One-to-zero-or-one relationship where authenticated requests include JWT token
- Token validation determines authenticated_user property of request

## Security Constraints

### Access Control Matrix
- Unauthenticated requests → 401 Unauthorized
- Valid token + Own resource → Allow access
- Valid token + Other user's resource → 403 Forbidden
- Invalid token → 401 Unauthorized

### Token Validation Requirements
- All API endpoints require valid JWT token (except public endpoints like health checks)
- Token must not be expired at time of request
- User ID in token must match user ID in URL path for user-specific operations
- Tokens must be verified using shared BETTER_AUTH_SECRET

### Data Isolation Rules
- Users can only access tasks where user_id matches their authenticated user_id
- Backend queries must filter by user_id for all user-specific data retrieval
- API responses must not contain data belonging to other users under any circumstance