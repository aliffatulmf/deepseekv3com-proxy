import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union


@dataclass
class SSEDataChunk:
    content: Dict[str, Any]


@dataclass
class SSEDoneChunk:
    pass


class SSEChunkType(Enum):
    DATA = "data"
    DONE = "done"


class SSEParseError(Exception):

    pass


SSEChunkV2 = Union[SSEDataChunk, SSEDoneChunk]

DONE_MARKER = "[DONE]"
DATA_PREFIX = "data"
SEPARATOR = ":"


def parse_sse_chunk(line: str) -> Optional[SSEChunkV2]:
    if not isinstance(line, str):
        raise SSEParseError("Input must be string")

    if not line.strip():
        return None

    try:
        field, value = line.split(SEPARATOR, 1)
    except ValueError:
        return None

    if field.strip() != DATA_PREFIX:
        return None

    value = value.strip()
    if not value:
        return None

    if value == DONE_MARKER:
        return SSEDoneChunk()

    try:
        data = json.loads(value)
        if not isinstance(data, dict):
            raise SSEParseError("JSON data must be an object")
        return SSEDataChunk(content=data.get("text", ""))
    except json.JSONDecodeError as e:
        raise SSEParseError(f"Invalid JSON: {str(e)}")
