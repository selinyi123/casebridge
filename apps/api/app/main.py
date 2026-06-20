from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.demo import router as demo_router

app = FastAPI(
    title="CaseBridge API",
    description="AI-Native Chinese social-work case-service and resource-collaboration system.",
    version="0.1.1-foundation-build",
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(demo_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "CaseBridge API",
        "version": "0.1.1-foundation-build",
        "rule": "AI assists, human confirms.",
    }
