from datetime import datetime
from typing import Any, Dict, Generator

import httpx
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from .browser_automation import run_web
from .chat_completion_state import (
    ChunkParams,
    DeltaContent,
    create_chunk,
    random_alphanum,
)
from .config import DEFAULT_MODEL, EFS, HEADERS, TARGET_URL
from .sse_handler import parse_sse_chunk
from .state import GTSM
from .util import DictMan

StreamOutput = Generator[ChatCompletionChunk, None, None]


def stream_response(response: ChatCompletionChunk) -> str:
    if not response.choices:
        return ""
    return f"data: {response.model_dump_json()}\n\n"


def sender(chunk: ChatCompletionChunk) -> Generator[str, None, None]:
    yield f"data: {chunk.model_dump_json()}\n\n"


def create_stream_params(
    model_name: str,
    index: int,
    delta_content: DeltaContent,
    system_fingerprint: str,
    conversation_id: str,
    finish_reason: str | None = None,
) -> ChunkParams:
    return ChunkParams(
        model_name=model_name,
        chunk_index=index,
        delta_content=delta_content,
        created_at=int(datetime.now().timestamp()),
        system_fingerprint=system_fingerprint,
        conversation_id=conversation_id,
        finish_reason=finish_reason,
    )


def sync_stream(request_data: Dict[Any, Any]) -> StreamOutput:
    system_fingerprint = f"fp_{random_alphanum(42, 10)}"
    conversation_id = f"chatcmpl-{random_alphanum(42, 10)}"

    while True:
        index = 0
        cookies, local_storage = GTSM.get_state()

        if local_storage.get("turnstileToken"):
            request_data["turnstileToken"] = local_storage["turnstileToken"]

        with httpx.stream(
            "POST",
            TARGET_URL,
            headers=HEADERS,
            json=request_data,
            cookies=cookies,
            timeout=None,
        ) as resp:
            if resp.status_code == 403:
                run_web()
                continue

            for line in resp.iter_lines():
                try:
                    chunk_data = parse_sse_chunk(line)
                    if chunk_data is None or not chunk_data.content:
                        continue

                    delta_content = DeltaContent(
                        role="assistant",
                        content=str(chunk_data.content),
                    )

                    params = create_stream_params(
                        model_name=DEFAULT_MODEL,
                        index=index,
                        delta_content=delta_content,
                        system_fingerprint=system_fingerprint,
                        conversation_id=conversation_id,
                    )

                    yield from sender(create_chunk(params))
                    index += 1
                except Exception as e:
                    print("GENERATOR EXCEPTION", e)
                    continue
            break

    final_params = create_stream_params(
        model_name=DEFAULT_MODEL,
        index=index,
        delta_content=DeltaContent(),
        system_fingerprint=system_fingerprint,
        conversation_id=conversation_id,
        finish_reason="stop",
    )

    yield from sender(create_chunk(final_params))
    yield EFS
