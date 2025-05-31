# Authentication System Notes

## Overview
The AI Assistant now has a complete authentication system with user roles and JWT tokens.

## Default Test Users
After running database migrations, these test users are available:
- **Admin**: username: `admin`, password: `admin123`, recovery PIN: `1234`
- **User**: username: `testuser`, password: `test123`

## First Time Setup
1. Start all services using `startai.bat`
2. Navigate to http://localhost:3000
3. You'll be redirected to `/login`
4. Use test credentials or click "Create Admin Account" for setup wizard

## Authentication Flow
1. **Login**: POST to `/api/auth/login` with username/password
2. **JWT Token**: Stored in HTTP-only cookie and localStorage
3. **Protected Routes**: All app routes require authentication
4. **Role-Based Access**: 
   - Admin: Full access to all features and models
   - User: Limited to Qwen model, no admin features

## Development Mode
To bypass authentication during development:
1. Edit `backend/app/core/config.py`
2. Set `dev_bypass_auth = True`
3. All requests will be treated as admin user

## Key Files
- **Backend**:
  - `app/core/auth.py` - JWT and password utilities
  - `app/api/endpoints/auth.py` - Login/logout endpoints
  - `app/api/deps.py` - Authentication dependencies
  - `app/db/models/user.py` - User model

- **Frontend**:
  - `src/services/authService.ts` - Auth API client
  - `src/context/AuthContext.tsx` - Global auth state
  - `src/components/auth/LoginPage.tsx` - Login UI
  - `src/components/auth/ProtectedRoute.tsx` - Route protection

## Security Notes
- Passwords are hashed with bcrypt
- JWT tokens expire after 48 hours
- Admin recovery PIN for password reset
- Self-aware mode now tied to admin role (no separate password)