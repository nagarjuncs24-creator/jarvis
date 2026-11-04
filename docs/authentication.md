# Authentication

JARVIS uses email/password registration with Argon2id password hashes. `POST /api/v1/auth/register` and `POST /api/v1/auth/login` issue a short-lived bearer access token and a refresh token.

Refresh tokens are represented in storage only by a SHA-256 fingerprint. Refreshing rotates the token and revokes the prior record. Clients send an access token in the `Authorization: Bearer <token>` header for protected routes. `GET /api/v1/auth/me` is the current authenticated-user verification endpoint.

Set a long, random `APP_SECRET_KEY` in the deployment secret store. The example development value is unsafe for shared or production environments.
