from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title=settings.app_name,
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
