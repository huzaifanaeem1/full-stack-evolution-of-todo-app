# Backend Setup Instructions

To run the backend server and complete the full application flow:

## Prerequisites
- Python 3.11+
- pip (Python package installer)
- PostgreSQL database (or Neon Serverless PostgreSQL)

## Current Status Check
First, let's check if the virtual environment is properly set up:

```bash
# Check if virtual environment exists and is functional
ls -la venv/bin/
# Look for python, pip executables

# Check if dependencies are installed
source venv/bin/activate && pip list
```

## Steps to Run Backend (if virtual environment needs setup)

1. **Navigate to the backend directory:**
   ```bash
   cd /mnt/d/evolution-of-todo/backend
   ```

2. **Check current Python and pip availability:**
   ```bash
   python3 --version
   python3 -m pip --version
   # If pip is not available, install it with: sudo apt install python3-pip
   ```

3. **Install Python virtual environment (if not already installed):**
   ```bash
   sudo apt update
   sudo apt install -y python3-venv
   ```

4. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Alternative: If sudo access is not available
If you don't have sudo access to install python3-venv, you may need to:
- Ask your system administrator to install python3-venv
- Or use a different environment where you have the necessary permissions

## Final Steps (once virtual environment is set up)
6. **Ensure environment variables are set in .env file:**
   - DATABASE_URL: Your PostgreSQL connection string
   - BETTER_AUTH_SECRET: A random secret string for JWT signing
   - BETTER_AUTH_URL: Your application's base URL
   - ENVIRONMENT: Environment (development/production)

   Note: These are already configured in the .env file in this directory.

7. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

8. **Start the backend server:**
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

9. **Verify the backend is running:**
   - Visit http://localhost:8000/ - should show "Welcome to the Todo Web Application API"
   - Visit http://localhost:8000/health - should show {"status": "healthy", "service": "todo-api"}

## Expected Behavior
Once the backend is running:
- The frontend (http://localhost:3000) can successfully register and login users
- API calls to http://localhost:8000/api will be successful
- The complete authentication flow will work end-to-end
- User registration, login, and task management will function properly