"""Тесты парсера: валидация схем и классификация content_type."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.parser.schemas import VKPost, VKWallGetResponse
from src.parser.vk_parser import _classify_content_type

FIXTURE = Path(__file__).parent / "fixtures" / "vk_response.json"


def test_vk_wall_response_parsed() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    resp = VKWallGetResponse.model_validate(data)
    assert resp.response.count == 3
    assert len(resp.response.items) == 3


def test_content_type_photo() -> None:
    attachments = [{"type": "photo"}]
    assert _classify_content_type(attachments) == "photo"


def test_content_type_video_priority_over_photo() -> None:
    attachments = [{"type": "video"}, {"type": "photo"}]
    assert _classify_content_type(attachments) == "video"


def test_content_type_link() -> None:
    attachments = [{"type": "link"}]
    assert _classify_content_type(attachments) == "link"


def test_content_type_text_when_no_attachments() -> None:
    assert _classify_content_type([]) == "text"


def test_content_type_priority_order() -> None:
    # video > photo > link > text
    assert _classify_content_type([{"type": "photo"}, {"type": "link"}]) == "photo"
    assert _classify_content_type([{"type": "link"}]) == "link"


def test_fixture_post_content_types() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    resp = VKWallGetResponse.model_validate(data)
    items = resp.response.items
    atts = [[a.model_dump() for a in p.attachments] for p in items]
    assert _classify_content_type(atts[0]) == "photo"   # только фото
    assert _classify_content_type(atts[1]) == "video"   # видео + фото → video
    assert _classify_content_type(atts[2]) == "text"    # нет вложений


def test_vk_post_defaults() -> None:
    post = VKPost(id=1, owner_id=-100, date=1700000000)
    assert post.likes.count == 0
    assert post.views.count == 0
    assert post.text == ""
    assert post.attachments == []
