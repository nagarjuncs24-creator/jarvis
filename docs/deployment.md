# Deployment

## Local stack

1. Copy `.env.example` to `.env`.
2. Set a unique `POSTGRES_PASSWORD`, a random 32+ character `APP_SECRET_KEY`, and the required provider credentials.
3. Start the stack with `docker compose up --build`.
4. Apply migrations with `docker compose exec backend alembic upgrade head`.

The services are exposed at frontend `:3000`, API `:8000`, PostgreSQL `:5432`, Redis `:6379`, and Qdrant `:6333`. Do not expose PostgreSQL, Redis, or Qdrant directly in a public deployment.

## Production checklist

- Use managed PostgreSQL, Redis, and Qdrant or private network services.
- Keep `.env` out of source control and inject secrets through the deployment platform.
- Set `APP_ENV=production` and a strong `APP_SECRET_KEY`.
- Configure HTTPS at the reverse proxy and set `FRONTEND_ORIGIN` to the deployed frontend origin.
- Run migrations as a release step before rolling out API instances.
- Replace the in-memory rate limiter with a Redis-backed limiter when horizontally scaling.
- Restrict storage, database, and vector-store access by network policy and least-privilege identities.

## CI

The GitHub Actions workflow runs backend tests and a frontend production build on pushes and pull requests.
