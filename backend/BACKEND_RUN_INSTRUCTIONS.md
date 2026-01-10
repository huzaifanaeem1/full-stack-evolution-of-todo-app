# Backend Server Setup and Run Instructions

## Current Status
The frontend is running successfully on http://localhost:3000, but the backend server is not running. API calls to http://localhost:8000/api are returning ERR_CONNECTION_REFUSED.

## Root Cause
The virtual environment cannot be created because the required `python3-venv` package is not installed on the system. This prevents the installation of backend dependencies.

## System Requirements (Critical)
Before the backend can be started, the following system packages must be installed:

```bash
# On Ubuntu/Debian systems:
sudo apt update
sudo apt install -y python3.12-venv python3-pip

# If you don't have sudo access, ask your system administrator to install these packages
```

## Complete Backend Setup Process

### Step 1: System Package Installation (Requires Sudo Access)
```bash
sudo apt update
sudo apt install -y python3.12-venv python3-pip
```

### Step 2: Navigate to Backend Directory
```bash
cd /mnt/d/evolution-of-todo/backend
```

### Step 3: Create and Activate Virtual Environment
```bash
# Create the virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### Step 4: Install Backend Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages from requirements.txt
pip install -r requirements.txt
```

### Step 5: Verify Environment Variables
The `.env` file is already configured in this directory with:
- DATABASE_URL: PostgreSQL connection string
- BETTER_AUTH_SECRET: JWT signing secret
- BETTER_AUTH_URL: http://localhost:3000
- ENVIRONMENT: development

### Step 6: Run Database Migrations
```bash
alembic upgrade head
```

### Step 7: Start the Backend Server
```bash
uvicorn src.main:app --reload --port 8000
```

## Expected Results
Once the backend is running:
- Visit http://localhost:8000/ - should show "Welcome to the Todo Web Application API"
- Visit http://localhost:8000/health - should show {"status": "healthy", "service": "todo-api"}
- API calls to http://localhost:8000/api will be successful
- The frontend authentication (register/login) will work end-to-end

## Troubleshooting
If you encounter issues:
1. Ensure the virtual environment is activated: `source venv/bin/activate`
2. Verify dependencies are installed: `pip list` (should show all packages from requirements.txt)
3. Check that the .env file has the correct values
4. Make sure port 8000 is available and not used by another process

## Current Environment Status
- Frontend: Running on http://localhost:3000 ✓
- Backend dependencies: Not installed ✗
- Virtual environment: Not properly created ✗
- Database migrations: Not run ✗
- Backend server: Not running ✗
- API endpoints: Not accessible ✗
- Authentication flow: Not working ✗