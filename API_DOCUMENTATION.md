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

Register a new user account. Users can optionally create a new company or join an existing one.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",  // Optional
  "company_name": "Acme Corp",  // Optional: Create new company or join existing
  "skills": "[\"Python\", \"Flask\"]",  // Optional
  "weekly_capacity": 40  // Optional
}
```

**Response (201) - New Company Created:**
```json
{
  "status": "success",
  "message": "Registration successful. Your company has been created and you can now login.",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "employee",
      "is_active": true,
      "is_verified": true,
      "company_id": 1
    },
    "requires_approval": false,
    "company_id": 1
  }
}
```

**Response (201) - Joining Existing Company:**
```json
{
  "status": "success",
  "message": "Registration successful. Your account is pending admin approval to join the company.",
  "data": {
    "user": {
      "id": 2,
      "email": "user2@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "role": "employee",
      "is_active": false,
      "is_verified": false,
      "company_id": 1
    },
    "requires_approval": true,
    "company_id": 1
  }
}
```

**Response (201) - No Company Specified:**
```json
{
  "status": "success",
  "message": "Registration successful. Your account is pending admin approval and company assignment.",
  "data": {
    "user": {
      "id": 3,
      "email": "user3@example.com",
      "first_name": "Bob",
      "last_name": "Johnson",
      "role": "employee",
      "is_active": false,
      "is_verified": false,
      "company_id": null
    },
    "requires_approval": true,
    "company_id": null
  }
}
```

**Notes:**
- If `company_name` is provided and company exists: User joins company (pending approval)
- If `company_name` is provided and company doesn't exist: New company is created, user is auto-activated
- If `company_name` is not provided: User account created without company (pending admin assignment)
- Users joining existing companies require admin approval
- Users creating new companies are automatically activated

---

### 1a. Register Company
**POST** `/auth/register-company`

Register a new company and create the admin user.

**Request Body:**
```json
{
  "company_name": "Acme Corp",
  "email": "admin@acme.com",
  "password": "AdminPass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",  // Optional
  "company_email": "company@acme.com",  // Optional: Company-wide login email
  "company_password": "CompanyPass123"  // Optional: Company-wide login password
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Company registration successful. You can now login.",
  "data": {
    "user": {
      "id": 1,
      "email": "admin@acme.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "admin",
      "company_id": 1
    },
    "company": {
      "id": 1,
      "name": "Acme Corp",
      "company_email": "company@acme.com",
      "company_login_enabled": true
    }
  }
}
```

---

### 2. Login
**POST** `/auth/login`

Login and receive JWT token. Supports both individual user login and company-wide login.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "user_id": 123  // Optional: Required when using company login with multiple users
}
```

**Response (200) - Individual Login:**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user": { ... },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "login_type": "individual"
  }
}
```

**Response (200) - Company Login (Multiple Users):**
```json
{
  "status": "success",
  "message": "Company login successful - select user",
  "data": {
    "requires_user_selection": true,
    "users": [
      {
        "id": 1,
        "email": "user1@example.com",
        "full_name": "John Doe",
        "role": "employee"
      },
      {
        "id": 2,
        "email": "user2@example.com",
        "full_name": "Jane Smith",
        "role": "teamleader"
      }
    ],
    "company": {
      "id": 1,
      "name": "Acme Corp",
      "company_email": "company@acme.com"
    }
  }
}
```

**Response (200) - Company Login (Single User - Auto-selected):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user": { ... },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "login_type": "company"
  }
}
```

**Notes:**
- If logging in with company credentials and multiple users exist, the API returns a list of users for selection
- If only one user exists, the login completes automatically
- After user selection, send another login request with `user_id` parameter

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

### 5. Get Company Settings
**GET** `/auth/company-settings`

Get company settings (Admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Company settings retrieved",
  "data": {
    "id": 1,
    "name": "Acme Corp",
    "company_email": "company@acme.com",
    "company_login_enabled": true,
    "subscription_status": "active"
  }
}
```

---

### 6. Update Company Settings
**PUT** `/auth/company-settings`

Update company settings including company-wide login credentials (Admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "company_email": "company@acme.com",  // Optional
  "company_password": "CompanyPass123",  // Optional (leave empty to keep current)
  "company_login_enabled": true          // Optional
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Company settings updated",
  "data": {
    "id": 1,
    "name": "Acme Corp",
    "company_email": "company@acme.com",
    "company_login_enabled": true
  }
}
```

---

### 7. Refresh Token
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