from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent_travel.api.errors import register_exception_handlers
from agent_travel.api.routes.chat import router as chat_router
from agent_travel.api.routes.miles import router as miles_router

app = FastAPI(title="agent-travel", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(chat_router)
app.include_router(miles_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
