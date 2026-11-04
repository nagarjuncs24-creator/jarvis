# Architecture

JARVIS is a monorepo composed of a Next.js frontend and FastAPI backend. PostgreSQL stores transactional and user-owned records, Redis provides transient coordination, and Qdrant is reserved for semantic retrieval. The API is the only service authorized to access infrastructure, LLM providers, and external integrations.

The initial application exposes liveness and readiness probes. Feature modules are added only alongside authorization, input validation, audit events, and tests.
