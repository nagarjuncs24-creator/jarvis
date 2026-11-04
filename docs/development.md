# Development standards

- Never add API keys to tracked files.
- Add a migration for every persistent schema change.
- Every user-owned query must be scoped by the authenticated user identifier.
- Tools accept structured inputs, enforce permissions, and cannot execute arbitrary shell commands.
- Sensitive actions require a persisted approval before execution.
- Add tests with each behavior change.
- Production deployments must supply an `APP_SECRET_KEY` of at least 32 random characters; startup rejects the development default.
- API responses include baseline browser security headers and an in-memory development rate limit. Deploy Redis-backed distributed rate limits when running multiple API workers.
