import functools
import multiprocessing as mp
import warnings
from json import JSONEncoder
from json import dumps as json_encode
from json import loads as json_decode
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    ParamSpec,
    Self,
    Set,
    Tuple,
    TypeVar,
    Union,
)

P = ParamSpec("P")
R = TypeVar("R")


class ExperimentalWarning(Warning):
    pass


def experimental(
    message: str = None,
    since_version: str = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Get class name if method is bound to a class
            if args and hasattr(args[0], "__class__"):
                qualified_name = f"{args[0].__class__.__name__}.{func.__name__}"
            else:
                qualified_name = func.__name__

            parts: List[str] = [
                f"The function `{qualified_name}` is experimental and may cause unexpected behavior.",
            ]

            if since_version:
                parts.append(f"since v{since_version}")
            if message:
                parts.append(message)

            warning_message = ". ".join(parts)
            warnings.warn(warning_message, ExperimentalWarning, stacklevel=2)
            return func(*args, **kwargs)

        wrapper.__experimental__ = True
        wrapper.__since_version__ = since_version
        return wrapper

    return decorator


T = TypeVar("T")


class DictMan:
    """ """

    def __init__(self, object: Union[Dict[str, Any] | T]) -> None:
        self.object: Union[Dict[str, Any] | T] = object
        self._include: Set[str] = set()
        self._exclude: Set[str] = set()
        self._cached_keys: Set[str] = set(object.keys())

    def exclude(self, keys: List[str]) -> Self:
        assert isinstance(keys, list)

        if any([key in self._include for key in keys]):
            raise ValueError("Keys to exclude cannot be in keys to include")

        self._exclude = set(keys)
        return self

    def include(self, keys: List[str]) -> Self:
        assert isinstance(keys, list)

        if any([key in self._exclude for key in keys]):
            raise ValueError("Keys to include cannot be in keys to exclude")

        self._include = set(keys)
        return self

    @functools.lru_cache(maxsize=128)
    def _clean_filter_keys(self, key: str) -> bool:
        if self._include and key not in self._include:
            return False
        if self._exclude and key in self._exclude:
            return False
        return True

    def clean(self, batch_size: int = 1000) -> Union[Dict[str, Any] | T]:
        obj = {}
        keys = list(self._cached_keys)

        # process in batches
        for i in range(0, len(keys), batch_size):
            batch = keys[i : i + batch_size]
            obj.update({k: self.object[k] for k in batch if self._clean_filter_keys(k)})

        return obj

    @experimental()
    def merge(
        self,
        other: Union[Dict[str, Any] | T],
        skip_existing: bool = True,
        deep_merge: bool = False,
    ) -> Self:
        if not isinstance(other, dict):
            raise TypeError("Merge operation requires dictionary")

        obj = self.object.copy()

        try:

            for key, value in other.items():
                if skip_existing and key in obj:
                    continue

                # fmt: off
                if deep_merge and isinstance(value, dict) and isinstance(obj.get(key), dict):
                    obj[key] = self._deep_merge(obj[key], value)
                else:
                    obj[key] = value
                # fmt: on

            self.object = obj
            return self

        except Exception as e:
            raise ValueError(f"Failed to merge dictionaries: {str(e)}")

    def _deep_merge(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        result = a.copy()

        # fmt: off
        for key, value in b.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        # fmt: on

        return result

    def from_json(self, json_str: str) -> Self:
        try:
            if not isinstance(json_str, str):
                raise ValueError("Invalid JSON string")

            self.object = json_decode(json_str)
            return self
        except (TypeError, ValueError) as e:
            raise ValueError(f"Error decoding JSON string: {e}")

    def to_json(
        self,
        pretty: bool = False,
        encoder: Optional[JSONEncoder] = None,
    ) -> str:
        try:
            if not self.object:
                raise ValueError("No dictionary to convert to JSON")

            return json_encode(
                self.object,
                indent=4 if pretty else None,
                cls=encoder,
                ensure_ascii=False,
            )
        except (TypeError, ValueError) as e:
            raise ValueError(f"Error encoding object to JSON: {e}")
