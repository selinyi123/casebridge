from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.seed import seed_demo_data
from app.db.session import SessionLocal, init_db
from app.routers.ai import router as ai_router
from app.routers.cases import router as cases_router
from app.routers.clients import router as clients_router
from app.routers.demo import router as demo_router
from app.routers.goals import router as goals_router
from app.routers.health import router as health_router
from app.routers.referrals import router as referrals_router
from app.routers.resources import router as resources_router
from app.routers.timeline import router as timeline_router

app = FastAPI(
    title="CaseBridge API",
    description="CaseBridge social-work case-service API.",
    version="0.1.8-redaction-apply-preview",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def bootstrap_database() -> None:
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)


app.include_router(health_router, prefix="/api/v1")
app.include_router(demo_router, prefix="/api/v1")
app.include_router(clients_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(goals_router, prefix="/api/v1")
app.include_router(referrals_router, prefix="/api/v1")
app.include_router(resources_router, prefix="/api/v1")
app.include_router(timeline_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "CaseBridge API",
        "version": "0.1.8-redaction-apply-preview",
        "rule": "Redaction gate and apply preview protect formal case fields.",
    }
