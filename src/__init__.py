from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api


def create_app():
    app = FastAPI(
        title="Llama-3-QuipuBase",
        description="A clone of the OpenAI API",
        version="0.1.0",
    )
    app.include_router(api)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
