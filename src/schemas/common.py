from typing import Optional

from pydantic import Field

from ..data import RocksDBModel


class User(RocksDBModel):
    email: Optional[str] = Field(
        default=None, title="Email", description="The user's email address."
    )
    email_verified: Optional[bool] = Field(
        default=None,
        title="Email Verified",
        description="Whether the user's email is verified.",
    )
    family_name: Optional[str] = Field(
        default=None, title="Family Name", description="The user's family name."
    )
    given_name: Optional[str] = Field(
        default=None, title="Given Name", description="The user's given name."
    )
    locale: Optional[str] = Field(
        default=None, title="Locale", description="The user's locale."
    )
    name: str = Field(..., title="Name", description="The user's full name.")
    nickname: Optional[str] = Field(
        default=None, title="Nickname", description="The user's nickname."
    )
    picture: Optional[str] = Field(
        default=None, title="Picture", description="URL of the user's picture."
    )
    sub: str = Field(
        ...,
        title="Subject Identifier",
        description="The subject identifier for the user.",
    )
    updated_at: Optional[str] = Field(
        default=None,
        title="Updated At",
        description="Timestamp of when the user's information was last updated.",
    )
