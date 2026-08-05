"""
JSON-safe serialization helpers for persisting domain objects
to SQLite.

Supports dataclasses, pydantic models, enums, datetimes and
nested containers (list / tuple / dict / set).
"""

import dataclasses
import typing
from datetime import datetime
from enum import Enum


def to_jsonable(value):
    """
    Converts a domain value into a JSON-serializable structure.
    """

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): to_jsonable(item)
            for key, item in value.items()
        }

    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: to_jsonable(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }

    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")

    return str(value)


def from_jsonable(data, cls=typing.Any):
    """
    Rebuilds a domain value from JSON using its type hint.

    Falls back to returning ``data`` unchanged when the target
    type is unknown or the conversion is not supported.
    """

    if data is None:
        return None

    if cls is typing.Any or cls is None:
        return data

    origin = typing.get_origin(cls)
    args = typing.get_args(cls)

    # Optional[X] / Union types
    if origin is typing.Union:
        non_none = [
            arg for arg in args if arg is not type(None)
        ]
        if len(non_none) == 1:
            return from_jsonable(data, non_none[0])
        for arg in args:
            try:
                return from_jsonable(data, arg)
            except Exception:
                continue
        return data

    # list / tuple / set containers
    if origin in (list, set, typing.List, typing.Set):
        element = args[0] if args else typing.Any
        converted = [
            from_jsonable(item, element) for item in data
        ]
        return set(converted) if origin is set else converted

    if origin is tuple or origin is typing.Tuple:
        element = args[0] if args else typing.Any
        return tuple(
            from_jsonable(item, element) for item in data
        )

    # dict containers
    if origin in (dict, typing.Dict):
        value_type = args[1] if len(args) > 1 else typing.Any
        return {
            key: from_jsonable(item, value_type)
            for key, item in data.items()
        }

    if not isinstance(cls, type):
        return data

    if issubclass(cls, Enum):
        return cls(data)

    if cls is datetime:
        return datetime.fromisoformat(data)

    if hasattr(cls, "model_validate"):
        return cls.model_validate(data)

    if dataclasses.is_dataclass(cls):
        hints = typing.get_type_hints(cls)
        kwargs = {}
        for field in dataclasses.fields(cls):
            if field.name not in data:
                continue
            kwargs[field.name] = from_jsonable(
                data[field.name],
                hints.get(field.name, field.type),
            )
        return cls(**kwargs)

    if cls in (str, int, float, bool):
        return cls(data)

    return data
