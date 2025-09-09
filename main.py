from fastapi import FastAPI
from fastapi.requests import Request
from config import Settings

from controllers.genre import router as genre_router

settings = Settings()

app = FastAPI(title="MultiTasker API", version=settings.VERSION)
app.include_router(genre_router)


@app.get("/")
async def main(request: Request):
    return {"message": "Hello World"}