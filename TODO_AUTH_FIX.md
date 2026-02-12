/,k# Authentication Fixes - TODO

## Issues Fixed:

1. [x] Signup - Return token from register to auto-login user
2. [x] Login.jsx - Fix user.name to use first_name + last_name
3. [x] Backend config - Allow development mode without SECRET_KEY env var
4. [x] Signup.jsx - Update to handle auto-login with token
5. [x] Signup.jsx - Support both snake_case and camelCase field names

## Remaining Tasks:

- [ ] Test the authentication flow
- [ ] Verify CORS configuration includes your Vite dev server port (typically 5173)
