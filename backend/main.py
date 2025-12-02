from datetime import datetime, UTC

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware


from backend.config import Settings
from backend.controllers.user import router as user_router
from backend.controllers.genre import router as genre_router

settings = Settings()

app = FastAPI(title="Books API", version=settings.VERSION)
app.include_router(user_router)
app.include_router(genre_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def main(request: Request):
    return {"message": f"Server on line. Time (UTC): {datetime.now(UTC)}"}
