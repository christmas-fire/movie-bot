from fastapi import FastAPI

from .users import router as users_router

app = FastAPI(
    title="Coffee Bot API",
    description="API для управления ботом и просмотра заказов",
    version="1.0.0"
)

app.include_router(users_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
