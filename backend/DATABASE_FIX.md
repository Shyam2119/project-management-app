# Database Fix Instructions

## Problem
If you encounter errors like:
```
sqlite3.OperationalError: no such column: users.company_id
```

This means your database schema is out of date and needs to be recreated.

## Solution

### Option 1: Use the Fix Script (Recommended)

1. **Stop the Flask server** if it's running (Ctrl+C)

2. **Run the fix script:**
   ```bash
   cd backend
   python fix_database.py
   ```

3. When prompted, type `yes` to confirm (this will delete all existing data)

4. The script will:
   - Drop all existing tables
   - Create new tables with correct schema
   - Verify the schema is correct
   - Create default admin user (admin@example.com / admin123)

5. **Start the Flask server again:**
   ```bash
   python run.py
   ```

### Option 2: Manual Fix

1. **Stop the Flask server** if it's running

2. **Delete the database file:**
   ```bash
   cd backend
   # On Windows:
   del project_management.db
   # On Mac/Linux:
   rm project_management.db
   ```

3. **Recreate the database:**
   ```bash
   python init_db.py
   ```

4. **Start the Flask server:**
   ```bash
   python run.py
   ```

## Verification

After fixing, you should be able to:
- Register a new company
- Login with admin@example.com / admin123
- Create users, projects, and tasks

## Important Notes

⚠️ **WARNING**: Both methods will **DELETE ALL EXISTING DATA** in the database!

If you have important data, you should:
1. Export it first (if possible)
2. Or manually migrate the data after recreating the schema

## Schema Changes

The current schema includes:
- `users.company_id` - Links users to companies
- `companies.company_email` - Company-wide login email
- `companies.company_password_hash` - Company-wide login password
- `companies.company_login_enabled` - Enable/disable company login

All other standard fields are also included.

