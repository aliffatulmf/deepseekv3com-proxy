from __future__ import annotations

from httpx import Cookies

from .types import LocalStorageKV


class TempState:
    cookies: Cookies = Cookies()
    local_storage = LocalStorageKV()

    @classmethod
    def set_state(cls, cookie: Cookies, local_storage: LocalStorageKV) -> None:
        cls.cookies = cookie
        cls.local_storage = local_storage

    @classmethod
    def get_state(cls) -> tuple[Cookies, LocalStorageKV]:
        return cls.cookies, cls.local_storage


# Global Temporary State Management
GTSM = TempState()
