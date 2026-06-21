from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.cases import router as cases_router
from app.routers.clients import router as clients_router
from app.routers.demo import router as demo_router
from app.routers.health import router as health_router
from app.routers.resources import router as resources_router

app = FastAPI(
    title="CaseBridge API",
    description="AI-Native Chinese social-work case-service and resource-collaboration system.",
    version="0.1.2-business-skeleton",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(demo_router, prefix="/api/v1")
app.include_router(clients_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(resources_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "CaseBridge API",
        "version": "0.1.2-business-skeleton",
        "rule": "Business loop first. AI later.",
    }
