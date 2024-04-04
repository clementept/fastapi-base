# FastAPI Project

This project is built with FastAPI and provides a set of endpoints for various functionalities such as user authentication, health checks, and user management.

## Overview

This project requires a PostgreSQL database server to be running. Ensure you have PostgreSQL installed and running on your system before proceeding.

## Environment Variables

### PostgreSQL Configuration

To connect to the PostgreSQL database, set the following environment variables:

- `DATABASE_HOSTNAME`: Hostname or IP address of the PostgreSQL server.
- `DATABASE_PORT`: Port number on which the PostgreSQL server is listening.
- `DATABASE_NAME`: Name of the main database.
- `DATABASE_USERNAME`: Username for accessing the database.
- `DATABASE_PASSWORD`: Password for accessing the database.

### Application Configuration

Additionally, set the following environment variables for configuring the application:

- `TEST_DATABASE_NAME`: Name of the test database.
- `ADMIN_EMAIL`: Email address for the admin user.
- `ADMIN_PASSWORD`: Password for the admin user.
- `JWT_SECRET_KEY`: Secret key for JWT (JSON Web Tokens) authentication.
- `JWT_ALGORITHM`: Algorithm used for JWT authentication.
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Expiry time for JWT access tokens (in minutes).
- `JWT_REFRESH_TOKEN_EXPIRE_MINUTES`: Expiry time for JWT refresh tokens (in minutes).
- `CORS_ALLOWED_ORIGINS`: List of allowed origins for CORS (Cross-Origin Resource Sharing).

Create a `.env` file in the project root directory and set these environment variables accordingly.

## Usage

To run the project, follow these steps:

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```


2. **Run migrations:**
   ```bash
   alembic upgrade head
   ```


3. **Run the project:**
   ```bash
   uvicorn app.main:app --reload
   ```

After running the project, you can access the API at http://localhost:8000.

## Running tests
   To run the tests, run the following command:
   ```bash
   pytest
   ```

   To run tests with coverage, run:
   ```bash
   pytest --cov=. --cov-report html && open coverage_html_report/index.html
   ```
    
## Endpoints

This project provides the following endpoints:

- **Authorization:**
  - `/api/login`: POST - Authenticate a user.
  - `/api/logout`: GET - Logout the currently authenticated user.
  - `/api/login/refresh`: GET - Refresh the authentication token.

- **Health:**
  - `/api/health`: GET - Check the health status of the application.

- **Users:**
  - `/api/users`: 
    - GET: Retrieve a list of users.
    - POST: Create a new user.
  - `/api/users/me`: GET - Retrieve details of the currently authenticated user.
  - `/api/users/activate`: POST - Activate a user account.
  - `/api/users/{id}`: GET - Retrieve details of a specific user by ID.

For detailed documentation and interactive exploration of these endpoints, please visit [http://localhost:8000/docs](http://localhost:8000/docs).







