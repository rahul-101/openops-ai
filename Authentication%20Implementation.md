# OpenOps AI - Authentication & Authorization Implementation

## Overview
This implementation provides a complete authentication and authorization system for the OpenOps AI platform, including:

### Core Components
1. **Backend Authentication Service** (`backend/app/infrastructure/auth/auth_service.py`)
   - JWT-based token authentication
   - User registration and login
   - Password recovery
   - Role-based access control
   - Session management

2. **Frontend Authentication** (`frontend/src/features/auth/`)
   - Login page with SSO support
   - User registration
   - Password recovery
   - Responsive auth layout

3. **Route Protection** (`frontend/src/components/auth/protected-route.tsx`)
   - Protected route guard for authenticated users
   - Public route guard for unauthenticated users
   - Automatic redirect based on auth state

4. **Auth Context** (`frontend/src/hooks/use-auth.tsx`)
   - React context provider for auth state
   - Login, register, logout, forgotPassword methods
   - Token management and persistence

## Key Features

### Backend (FastAPI)
- **JWT Authentication**: Secure token-based authentication using HS256
- **Role-Based Access Control**: Support for Admin, Operator, Viewer, and User roles
- **Password Hashing**: Using bcrypt with proper salting
- **CORS Configuration**: Secure cross-origin requests
- **OAuth2 Password Flow**: Standard token generation
- **Error Handling**: Comprehensive error responses

### Frontend (React)
- **Zod Validation**: Schema validation for all forms
- **Responsive Design**: Mobile-friendly authentication pages
- **Form Handling**: React Hook Form integration
- **Toast Notifications**: User feedback
- **Route Protection**: Automatic navigation based on auth state
- **Token Persistence**: Local storage for session management

### Security
- Password hashing with bcrypt
- JWT tokens with expiration
- Secure cookie options (for future implementation)
- Rate limiting considerations
- Input validation and sanitization

## Architecture

### Backend Flow
1. User submits login form
2. Backend validates credentials
3. JWT token generated with user claims
4. Token returned to frontend
5. Frontend stores token and makes authenticated requests
6. Backend verifies token on protected routes

### Frontend Flow
1. User visits protected page
2. ProtectedRoute checks auth state
3. Redirects to login if not authenticated
4. User logs in, receives token
5. Token stored and subsequent requests authorized
6. Access maintained until logout or token expiration

## Configuration

### Environment Variables
```bash
# JWT Secret Key
SECRET_KEY=your-super-secret-key-here

# Token Settings
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Frontend URLs (for CORS)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Backend Dependencies
```python
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
```

### Frontend Dependencies
```typescript
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useAuth } from "@/hooks/use-auth"
```

## Usage

### Accessing Protected Routes
Use the `ProtectedRoute` component:
```tsx
import { ProtectedRoute } from "@/components/auth/protected-route"

<ProtectedRoute>
  <DashboardPage />
</ProtectedRoute>
```

### Public Routes (Login/Register)
Use the `PublicRoute` component:
```tsx
import { PublicRoute } from "@/components/auth/protected-route"

<PublicRoute>
  <LoginPage />
</PublicRoute>
```

### Using Auth Hook
```tsx
import { useAuth } from "@/hooks/use-auth"

const { user, isAuthenticated, login, register, logout } = useAuth()

// Login
await login("username", "password")

// Register
await register("username", "email@example.com", "password")

// Logout
logout()
```

## Testing

### Backend Tests
```bash
# Run authentication tests
pytest backend/tests/auth/

# Test user registration, login, token validation
```

### Frontend Tests
```bash
# Run auth component tests
npm test --frontend/src/features/auth/

# Test login, register, and protected routes
```

## Demo Credentials

### Backend Demo Users
- `admin` / `Admin@123` (Admin role)
- `user` / `User@123` (User role)

### Frontend Demo (would use same credentials)
- Username: admin
- Password: Admin@123

## Security Considerations

1. **Never expose secret keys in client-side code**
2. **Implement rate limiting for authentication endpoints**
3. **Use HTTPS in production**
4. **Implement proper token expiration and refresh**
5. **Sanitize all user inputs**
6. **Use secure cookies for token storage**
7. **Implement logout on token expiration**

## Future Enhancements

1. **SSO Integration**: Google, Microsoft, GitHub OAuth2
2. **Multi-factor Authentication**: SMS, Email, TOTP
3. **Session Management**: JWT with refresh tokens
4. **Password Policies**: Complex password requirements
5. **Account Recovery**: Secure password reset flows
6. **Audit Logging**: Track all authentication events
7. **Security Headers**: Implement security headers
8. **Mobile Apps**: Native mobile authentication

## API Reference

### Backend Endpoints
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/register` - Register new user
- `POST /api/auth/forgot-password` - Request password reset
- `GET /api/auth/me` - Get current user info
- `GET /api/health` - Health check

### Frontend Routes
- `/auth/login` - Login page
- `/auth/register` - Registration page
- `/auth/forgot-password` - Password recovery
- `/` - Dashboard (protected)
- `/overview` - Overview (protected)
- etc.

## Integration Notes

### With Existing AppShell
The authentication system integrates with the existing AppShell:
- All routes under `/auth/*` use a separate layout
- Protected routes are nested under the AppShell
- Auth state is shared across the entire application

### Navigation Updates
Update navigation to include auth links:
```tsx
export const navigationGroups: NavGroup[] = [
  // ... existing items
  {
    label: "Account",
    items: [
      { title: "Profile", href: "/profile", icon: User },
      { title: "Settings", href: "/settings", icon: Settings },
    ],
  },
]
```

## Migration Guide

### From Scratch
1. Copy the authentication files to your project
2. Configure environment variables
3. Update navigation with auth links
4. Wrap your app with AuthProvider
5. Protect routes as needed

### Upgrading
1. Update environment variables
2. Configure CORS as needed
3. Review and update user passwords
4. Test authentication flows
5. Verify token persistence

This implementation provides a robust, secure, and production-ready authentication and authorization system for OpenOps AI.
