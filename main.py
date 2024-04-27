from fastapi import Request

from src import create_app

app = create_app()


@app.get("/")
async def root(request: Request):
    return dict(request.headers)
