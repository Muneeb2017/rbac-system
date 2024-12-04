# Role-Based Access Control (RBAC) System

A robust RBAC system built with FastAPI and PostgreSQL, featuring comprehensive user management, role-based permissions, and audit logging.

## 🌟 Features

- **User Management**: Create and manage users with different roles
- **Role Management**: Pre-defined roles (staff, supervisor, admin) with customizable permissions
- **Permission System**: Granular control over resource access
- **Audit Logging**: Comprehensive tracking of all system access attempts
- **JWT Authentication**: Secure token-based authentication
- **API Documentation**: Full OpenAPI/Swagger documentation

## 🛠️ Technology Stack

- **Backend**: Python FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: OpenAPI (Swagger)
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- PostgreSQL (if running without Docker)

## ⚙️ Installation & Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/rbac-system.git
   cd rbac-system
   ```

2. Create .env file:

   ```bash
   DATABASE_URL=""
   JWT_SECRET_KEY=your-secret-key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. Build and start the containers:

   ```bash
   docker-compose up --build
   ```

4. Initialize the database:
   ```bash
   docker-compose exec web python -m app.utils.init_db
   ```

## 🔑 Default Admin Credentials

```
Username: admin
Password: admin123
```

## 🔄 API Endpoints

### Authentication

- POST `/token` - Get access token

### Users

- POST `/users/` - Create user
- GET `/users/` - List users
- GET `/users/{user_id}` - Get user details
- PUT `/users/{user_id}/roles` - Assign roles

### Roles

- GET `/roles/` - List roles
- GET `/roles/{role_id}` - Get role details
- PUT `/roles/{role_id}/permissions` - Assign permissions

### Permissions

- GET `/permissions/` - List permissions
- POST `/permissions/` - Create permission
- GET `/permissions/role/{role_id}` - List role permissions

### Audit Logs

- GET `/audit/logs` - Get audit logs
- GET `/audit/logs/summary` - Get audit summary
- GET `/audit/logs/export` - Export audit logs

## 📝 Development Setup

1. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:

   ```bash
   alembic upgrade head
   ```

4. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## 🧪 Testing

Run the test suite:

```bash
pytest
```

### Deployment Steps:

1. Fork this repository
2. Set up environment variables in your deployment platform
3. Deploy using the provided Dockerfile
