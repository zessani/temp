from enum import Enum

from pydantic import BaseModel


class ResumeWebLinkPlatform(str, Enum):
    GITHUB = "github"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    HANDSHAKE = "handshake"
    OTHER = "other"


class ResumeWebLink(BaseModel):
    url: str
    platform: ResumeWebLinkPlatform
