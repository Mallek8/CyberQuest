from dataclasses import asdict, is_dataclass
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def render(model: type[T], value: object) -> T:
    if is_dataclass(value) and not isinstance(value, type):
        return model.model_validate(asdict(value))
    return model.model_validate(value)
