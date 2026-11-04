from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness check that does not expose internal configuration."""
    return {"status": "ok", "service": "jarvis-api"}


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Foundation readiness endpoint; dependency checks arrive with persistence."""
    return {"status": "ready", "service": "jarvis-api"}
