from fastapi import FastAPI

from apps.api.routers.research import router as research_router


app = FastAPI(
    title="AgentLab API",
    version="1.0.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(
    research_router,
    prefix="/api/research",
)