import os
from functools import cached_property
from typing import Any
from uuid import uuid4

from boto3 import client
from fastapi import UploadFile
from pydantic import BaseModel, Field

from ..interfaces import IProxy
from ..utils.handlers import asyncify, get_logger, handle

logger = get_logger(__name__)


def _det_content_type(filename: str) -> str:
    ext = filename.split(".")[-1]
    if ext in ("jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "ico"):
        return f"image/{ext}"
    elif ext in ("mp4", "webm", "flv", "avi", "mov", "wmv", "mpg", "mpeg"):
        return f"video/{ext}"
    elif ext in ("mp3", "wav", "flac", "aac", "ogg", "wma", "m4a"):
        return f"audio/{ext}"
    elif ext in ("pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"):
        return f"application/{ext}"
    elif ext in ("zip", "tar", "gz", "rar", "7z"):
        return f"application/{ext}"
    elif ext in (
        "txt",
        "csv",
        "json",
        "xml",
        "yaml",
        "yml",
        "html",
        "htm",
        "css",
        "js",
        "ts",
        "jsx",
        "tsx",
        "md",
        "rst",
    ):
        return f"text/{ext}"
    else:
        return "text/x-python" if ext == "py" else "application/octet-stream"


class ObjectStorage(BaseModel, IProxy[Any]):
    """
    ObjectStorage class for interacting with the storage service.
    """

    bucket: str = Field(default="tera")

    def __load__(self):
        return client(
            service_name="s3",
            endpoint_url="https://storage.indiecloud.co",
            aws_access_key_id=os.environ.get("MINIO_ROOT_USER"),
            aws_secret_access_key=os.environ.get("MINIO_ROOT_PASSWORD"),
            region_name="us-east-1",
        )

    @cached_property
    def minio(self):
        """
        Get the minio client.
        """
        return self.__load__()

    @asyncify
    def put_object(self, *, key: str, data: bytes, content_type: str):
        """
        Put an object in the storage.
        """
        self.minio.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
            ACL="public-read",
        )

    @asyncify
    def generate_presigned_url(self, *, key: str, ttl: int = 3600):
        """
        Generate a presigned URL for the object.
        """
        return self.minio.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=ttl,
        )

    @handle
    async def put(self, *, key: str, file: UploadFile) -> str:
        """
        Put a file in the storage.
        """
        if not file.content_type and file.filename:
            content_type = _det_content_type(file.filename)
        elif not file.filename and file.content_type:
            content_type = file.content_type
        elif file.filename and file.content_type:
            content_type = file.content_type
        else:
            content_type = "application/octet-stream"
        key = (
            f"{key}_{uuid4().hex}_{file.filename}"
            if file.filename
            else f"{key}_{uuid4().hex}.wav"
        )
        data = await file.read()
        await self.put_object(key=key, data=data, content_type=content_type)
        return await self.generate_presigned_url(key=key)

    @handle
    async def get(self, *, key: str) -> str:
        """
        Get a file from the storage.
        """
        return await self.generate_presigned_url(key=key)

    @asyncify
    def remove_object(self, *, key: str):
        """
        Remove an object from the storage.
        """
        self.minio.delete_object(Bucket=self.bucket, Key=key)

    @handle
    async def remove(self, *, key: str):
        """
        Remove a file from the storage.
        """
        await self.remove_object(key=key)

    @asyncify
    def list_objects(self, *, key: str):
        """
        List objects in the storage.
        """
        return self.minio.list_objects(Bucket=self.bucket, Prefix=key)

    @handle
    async def list(self, *, key: str):
        """
        List files in the storage.
        """
        return await self.list_objects(key=key)
