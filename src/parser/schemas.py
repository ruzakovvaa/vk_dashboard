"""Pydantic-схемы для валидации ответов VK API."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class VKAttachment(BaseModel):
    type: str
    model_config = {"extra": "allow"}


class VKLikes(BaseModel):
    count: int = 0


class VKComments(BaseModel):
    count: int = 0


class VKReposts(BaseModel):
    count: int = 0


class VKViews(BaseModel):
    count: int = 0


class VKPost(BaseModel):
    id: int
    owner_id: int
    date: int  # unix timestamp
    text: str = ""
    post_type: str = "post"
    attachments: list[VKAttachment] = Field(default_factory=list)
    likes: VKLikes = Field(default_factory=VKLikes)
    comments: VKComments = Field(default_factory=VKComments)
    reposts: VKReposts = Field(default_factory=VKReposts)
    views: VKViews = Field(default_factory=VKViews)

    model_config = {"extra": "allow"}


class VKWallResponse(BaseModel):
    count: int
    items: list[VKPost]


class VKWallGetResponse(BaseModel):
    response: VKWallResponse


class VKGroup(BaseModel):
    id: int
    name: str = ""
    screen_name: str = ""
    members_count: int = 0

    model_config = {"extra": "allow"}


class VKGroupsResponseBody(BaseModel):
    groups: list[VKGroup] = Field(default_factory=list)
    model_config = {"extra": "allow"}


class VKGroupsResponse(BaseModel):
    response: list[VKGroup] | VKGroupsResponseBody

    @property
    def groups(self) -> list[VKGroup]:
        if isinstance(self.response, list):
            return self.response
        return self.response.groups
