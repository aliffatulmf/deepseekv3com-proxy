from typing import TypedDict


class LocalStorageKV(TypedDict):
    tokenExpiry: str
    chatMessages: str
    turnstileToken: str
