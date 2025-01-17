import random
import string
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, TypedDict

from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta

from .exception import ChoiceCreationError, ChunkCreationError

OBJECT_TYPE = "chat.completion.chunk"
DEFAULT_FINISH_REASON = None


class DeltaContentDict(TypedDict):
    role: Optional[str]
    content: Optional[str]
    function_call: Optional[Dict[str, Any]]
    tool_calls: Optional[list]


class DeltaContent(TypedDict):
    role: Optional[str]
    content: Optional[str]
    function_call: Optional[Dict[str, Any]]
    tool_calls: Optional[list]


@dataclass
class ChoiceParams:
    index: int
    delta_content: DeltaContentDict
    finish_reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.index, int) or self.index < 0:
            raise ChoiceCreationError("Index must be a non-negative integer")
        if not isinstance(self.delta_content, dict):
            raise ChoiceCreationError("Delta content must be a dictionary")
        if self.finish_reason is not None and not isinstance(self.finish_reason, str):
            raise ChoiceCreationError("Finish reason must be None or string")


@dataclass
class ChunkParams:
    model_name: str
    chunk_index: int
    delta_content: DeltaContent
    system_fingerprint: str
    conversation_id: str
    finish_reason: Optional[str] = DEFAULT_FINISH_REASON
    created_at: Optional[float] = None

    def __post_init__(self) -> None:
        if not isinstance(self.model_name, str) or not self.model_name:
            raise ChunkCreationError("Invalid model name")
        if not isinstance(self.chunk_index, int) or self.chunk_index < 0:
            raise ChunkCreationError("Invalid chunk index")
        if not isinstance(self.system_fingerprint, str) or not self.system_fingerprint:
            raise ChunkCreationError("Invalid system fingerprint")
        if not isinstance(self.conversation_id, str) or not self.conversation_id:
            raise ChunkCreationError("Invalid conversation ID")


def create_choice(params: ChoiceParams) -> Choice:
    try:
        return Choice(
            index=params.index,
            delta=ChoiceDelta(**params.delta_content),
            logprobs=None,
            finish_reason=params.finish_reason,
        )
    except Exception as e:
        raise ChoiceCreationError(f"Failed to create choice: {str(e)}")


def create_chunk(params: ChunkParams) -> ChatCompletionChunk:
    try:
        timestamp = int(params.created_at or time.time())

        return ChatCompletionChunk(
            id=params.conversation_id,
            object=OBJECT_TYPE,
            created=timestamp,
            model=params.model_name,
            system_fingerprint=params.system_fingerprint,
            choices=[
                create_choice(
                    ChoiceParams(
                        params.chunk_index,
                        params.delta_content,
                        params.finish_reason,
                    )
                )
            ],
        )
    except Exception as e:
        raise ChunkCreationError(f"Failed to create chunk: {str(e)}")


def random_alphanum(seed: int, length: int) -> str:
    inst = random.Random(seed)
    chars = string.ascii_lowercase + string.digits
    rand_str = "".join(inst.choices(chars, k=length))
    return rand_str
