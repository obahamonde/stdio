import os

import httpx
from fastapi import APIRouter, HTTPException, Request

from .schemas import User
from .tasks import LanguageModel
from .tasks.image import ImageGeneration, ImageRequest
from .tasks.llm import IRequest, LLMConversation, Thread
from .tasks.music import Music, MusicRequest
from .tasks.tts import YoutubeToText, YoutubeVideoRequest

api = APIRouter(prefix="/api")
AUTH0_URL = os.getenv("AUTH0_URL")


@api.post("/thread/{namespace}")
async def llm_endpoint_post(conversation: LLMConversation, namespace: str):
    previous = await Thread.find_many(namespace=namespace)
    if previous:
        conversation.messages = (
            previous[0].conversation.messages + conversation.messages
        )
    llm = LanguageModel(namespace=namespace, instructions=conversation.instructions)
    return await llm.handler(request=IRequest[LLMConversation](input=conversation))


@api.get("/thread/{namespace}")
async def llm_endpoint_get(namespace: str):
    return await Thread.find_many(namespace=namespace)


@api.post("/image")
async def image_endpoint(request: ImageRequest):
    return await ImageGeneration().handler(
        request=IRequest[ImageRequest](input=request)
    )


@api.post("/music")
async def music_endpoint(request: MusicRequest):
    return await Music().handler(request=IRequest[MusicRequest](input=request))


@api.post("/ytt")
async def ytt_endpoint(request: YoutubeVideoRequest):
    return await YoutubeToText().handler(
        request=IRequest[YoutubeVideoRequest](input=request)
    )


@api.get("/ytt")
async def ytt_endpoint_get(query: str):
    return await YoutubeToText().search(query=query)


@api.post("/auth")
async def auth_endpoint(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AUTH0_URL}/userinfo",
            headers={"Authorization": token},
        )
        response.raise_for_status()
        user = User(**response.json())
        sub = user.sub
        existing_user_wrapped = await User.find_many(sub=sub)
        if existing_user_wrapped:
            assert len(existing_user_wrapped) == 1, "Multiple users with same sub"
            existing_user = existing_user_wrapped[0]
            return existing_user
        await user.save()
        return user


@api.post("/twilio")
async def twiml_webhook(request: Request):
    with open("src/twiml.xml", "wb") as f:
        f.write(await request.body())
