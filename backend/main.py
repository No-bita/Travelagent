from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.chat import router as chat_router
from routers.healthcheck import router as health_router
from routers.metrics import router as metrics_router


def create_app() -> FastAPI:
    app = FastAPI(title="Flight Booking Chat Agent (MVP)")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(metrics_router)
    return app


app = create_app()


