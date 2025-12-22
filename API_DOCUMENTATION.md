# 🔐 Authentication API Documentation

Base URL: `http://localhost:5000/api`

---

## Table of Contents
1. [Authentication Endpoints](#authentication-endpoints)
2. [User Management Endpoints](#user-management-endpoints)
3. [Project Management Endpoints](#project-management-endpoints)

---

## Authentication Endpoints

### 1. Register User
**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "employee",
  "skills": ["Python", "Flask"],
  "weekly_capacity": 40
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "user": { ... },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

### 2. Login
**POST** `/auth/login`

Login and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user": { ... },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

### 3. Get Current User
**GET** `/auth/me`

Get authenticated user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "User profile retrieved",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "role": "employee",
      "skills": "[\"Python\", \"Flask\"]",
      "weekly_capacity": 40,
      "is_active": true
    }
  }
}
```

---

### 4. Change Password
**PUT** `/auth/change-password`

Change user password.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "current_password": "OldPass123",
  "new_password": "NewPass123"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Password changed successfully"
}
```

---

### 5. Refresh Token
**POST** `/auth/refresh`

Get a new JWT token.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

## User Management Endpoints

### 6. Get All Users
**GET** `/users/`

Get all users with pagination and filtering.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10)
- `role` (string): Filter by role (admin, manager, employee)
- `is_active` (boolean): Filter by active status
- `search` (string): Search by name or email

**Response (200):**
```json
{
  "status": "success",
  "message": "Users retrieved successfully",
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 50,
    "pages": 5
  }
}
```

---

### 7. Get User by ID
**GET** `/users/<user_id>`

Get specific user details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "User retrieved successfully",
  "data": {
    "user": { ... }
  }
}
```

---

### 8. Update User
**PUT** `/users/<user_id>`

Update user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "phone": "+9876543210",
  "skills": ["New", "Skills"],
  "weekly_capacity": 35
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "User updated successfully",
  "data": {
    "user": { ... }
  }
}
```

---

### 9. Delete User (Admin Only)
**DELETE** `/users/<user_id>`

Delete a user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "User deleted successfully"
}
```

---

### 10. Deactivate User (Admin/Manager)
**PUT** `/users/<user_id>/deactivate`

Deactivate a user account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "User deactivated successfully"
}
```

---

### 11. Get User Workload
**GET** `/users/<user_id>/workload`

Get user's current workload and bandwidth.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "User workload retrieved",
  "data": {
    "user_id": 1,
    "user_name": "John Doe",
    "weekly_capacity": 40,
    "current_workload": 35,
    "available_capacity": 5,
    "utilization_percentage": 87.5,
    "is_overloaded": false
  }
}
```

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "status": "error",
  "message": "Invalid request",
  "errors": { ... }
}
```

**401 Unauthorized:**
```json
{
  "status": "error",
  "message": "Invalid credentials"
}
```

**403 Forbidden:**
```json
{
  "status": "error",
  "message": "Access denied"
}
```

**404 Not Found:**
```json
{
  "status": "error",
  "message": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "status": "error",
  "message": "Server error"
}
```

---

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

---

## Role-Based Access

- **Admin**: Full access to all resources
- **Manager**: Can manage projects, tasks, and view all users
- **Employee**: Can view assigned tasks and update own profile