"""Обёртка над VK API с rate-limiting и retry-логикой."""
from __future__ import annotations

import time
from typing import Any

import httpx
from loguru import logger

from src.config import settings

VK_API_BASE = "https://api.vk.com/method"
_MIN_INTERVAL = 0.34  # ~3 req/s для пользовательских токенов


class VKAPIError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"VK API error {code}: {message}")
        self.code = code


class VKClient:
    """Синхронный HTTP-клиент для VK API."""

    def __init__(
        self,
        token: str | None = None,
        api_version: str | None = None,
        max_retries: int = 3,
    ) -> None:
        self._token = token or settings.vk_access_token
        self._version = api_version or settings.vk_api_version
        self._max_retries = max_retries
        self._last_request_at: float = 0.0
        self._client = httpx.Client(timeout=30.0)

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < _MIN_INTERVAL:
            time.sleep(_MIN_INTERVAL - elapsed)

    def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Вызов метода VK API с retry при ошибках 6 и 5xx."""
        url = f"{VK_API_BASE}/{method}"
        payload = {
            "access_token": self._token,
            "v": self._version,
            **(params or {}),
        }
        delay = 1.0
        for attempt in range(1, self._max_retries + 1):
            self._throttle()
            self._last_request_at = time.monotonic()
            try:
                resp = self._client.post(url, data=payload)
                resp.raise_for_status()
                data: dict[str, Any] = resp.json()
            except httpx.HTTPError as exc:
                logger.warning(f"HTTP error on attempt {attempt}/{self._max_retries}: {exc}")
                if attempt == self._max_retries:
                    raise
                time.sleep(delay)
                delay *= 2
                continue

            if "error" in data:
                err = data["error"]
                code = err.get("error_code", -1)
                msg = err.get("error_msg", "unknown")
                logger.warning(f"VK error {code} on attempt {attempt}: {msg}")
                if code == 6 or code >= 500:
                    # Too many requests or server error — retry
                    if attempt == self._max_retries:
                        raise VKAPIError(code, msg)
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise VKAPIError(code, msg)

            logger.debug(f"VK API {method} OK (attempt {attempt})")
            return data

        raise VKAPIError(-1, "Max retries exceeded")

    def groups_get_by_id(self, screen_name: str) -> dict[str, Any]:
        """Получить метаданные сообщества по screen_name."""
        result = self.call(
            "groups.getById",
            {"group_ids": screen_name, "fields": "members_count"},
        )
        return result

    def wall_get(self, owner_id: int, count: int = 100, offset: int = 0) -> dict[str, Any]:
        """Получить публикации со стены сообщества."""
        return self.call(
            "wall.get",
            {"owner_id": owner_id, "count": count, "offset": offset, "extended": 0},
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> VKClient:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
