from fastapi import APIRouter


router = APIRouter()


@router.get("/ok")
async def healthcheck() -> dict:
    """Healthcheck endpoint."""
    return {"status": "up"}
