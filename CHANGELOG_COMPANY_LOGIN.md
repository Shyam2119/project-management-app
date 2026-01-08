# Company-Wide Login Feature - Changelog

## Overview
Added comprehensive company-wide authentication system that allows companies to set shared credentials (company email and password) that all users in the company can use to login. This feature provides flexibility for organizations that want to use shared credentials while maintaining individual user accounts.

## Backend Changes

### 1. Company Model (`backend/app/models/company.py`)
- **Added Fields:**
  - `company_email`: Unique email for company-wide login
  - `company_password_hash`: Hashed password for company login
  - `company_login_enabled`: Boolean flag to enable/disable company login

- **Added Methods:**
  - `set_company_password(password)`: Hash and store company password
  - `check_company_password(password)`: Verify company password
  - `to_dict(include_sensitive=False)`: Serialize company data
  - `find_by_company_email(email)`: Static method to find company by email

### 2. Authentication Routes (`backend/app/routes/auth.py`)
- **Enhanced `/auth/login` endpoint:**
  - Now supports both individual user login and company-wide login
  - Checks company credentials first, then falls back to individual user login
  - Returns user list for selection when company login has multiple users
  - Auto-selects user if only one user exists in company
  - Supports `user_id` parameter for company login user selection

- **Enhanced `/auth/register-company` endpoint:**
  - Now accepts optional `company_email` and `company_password` during registration
  - Automatically enables company login if credentials are provided

- **New Endpoints:**
  - `GET /auth/company-settings`: Get company settings (Admin only)
  - `PUT /auth/company-settings`: Update company settings including credentials (Admin only)

## Frontend Changes

### 1. Auth Context (`frontend/src/contexts/AuthContext.jsx`)
- **Enhanced `login` function:**
  - Now handles company login with user selection
  - Returns `requiresUserSelection` flag when multiple users exist
  - Returns user list and company info for selection screen

- **New Function:**
  - `loginWithUserSelection(credentials, selectedUserId)`: Complete login after user selection

### 2. Login Page (`frontend/src/pages/Login.jsx`)
- **Added Features:**
  - User selection screen for company login with multiple users
  - Beautiful UI for selecting user account after company login
  - Support for both individual and company login in same form
  - Updated placeholder text to indicate company login support

### 3. Settings Page (`frontend/src/pages/Settings.jsx`)
- **New Section (Admin Only):**
  - Company Settings panel
  - Toggle to enable/disable company login
  - Input fields for company email and password
  - Password visibility toggle
  - Success/error notifications
  - Real-time settings update

### 4. Admin Signup Page (`frontend/src/pages/auth/AdminSignup.jsx`)
- **Added Features:**
  - Optional collapsible section for company credentials
  - Fields for company email and password during registration
  - Helpful descriptions and placeholders

### 5. API Service (`frontend/src/services/api.js`)
- **New API Methods:**
  - `authAPI.getCompanySettings()`: Fetch company settings
  - `authAPI.updateCompanySettings(data)`: Update company settings

## Database Schema Changes

### Companies Table
New columns added:
- `company_email` (VARCHAR(120), UNIQUE, NULLABLE)
- `company_password_hash` (VARCHAR(255), NULLABLE)
- `company_login_enabled` (BOOLEAN, DEFAULT FALSE)

**Note:** These fields are nullable and have defaults, so existing databases will work without migration. New installations will include these fields automatically.

## API Documentation Updates

Updated `API_DOCUMENTATION.md` with:
- Enhanced login endpoint documentation
- Company settings endpoints documentation
- Register company endpoint with optional credentials
- Response examples for all scenarios

## Usage

### For Administrators

1. **Setting Up Company Login:**
   - Go to Settings page (Admin only)
   - Enable "Company Login" toggle
   - Enter company email (e.g., `company@acme.com`)
   - Set company password
   - Click "Save Company Settings"

2. **During Company Registration:**
   - Fill in company registration form
   - Expand "Company-Wide Login (Optional)" section
   - Enter company email and password
   - These will be automatically configured

### For Users

1. **Individual Login:**
   - Use personal email and password as before
   - Works exactly as it did before

2. **Company Login:**
   - Use company email and company password
   - If multiple users exist, select your account from the list
   - If only one user exists, login completes automatically

## Benefits

1. **Flexibility:** Companies can choose to use shared credentials or individual accounts
2. **Security:** Company passwords are hashed using bcrypt
3. **User Experience:** Seamless login flow with automatic user selection when possible
4. **Administration:** Easy management through Settings page
5. **Backward Compatible:** Existing individual logins continue to work

## Security Considerations

- Company passwords are hashed using bcrypt (same as user passwords)
- Company email must be unique across all companies
- Company login can be enabled/disabled by admins
- Individual user logins remain independent and secure
- All authentication follows the same security patterns as before

## Testing Recommendations

1. Test individual user login (should work as before)
2. Test company login with single user (should auto-select)
3. Test company login with multiple users (should show selection screen)
4. Test company settings update (admin only)
5. Test company registration with credentials
6. Test disabling company login
7. Test password validation for company passwords

## Future Enhancements (Optional)

- Password reset for company credentials
- Audit log for company login usage
- Multiple company email aliases
- Time-based access restrictions for company login
- IP whitelisting for company login

