"""
Generic paginated response DTOs.
"""

from typing import Generic, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    """
    Standard paginated API response.
    """

    items: list[T]

    page: int

    size: int

    total_items: int

    total_pages: int

    has_next: bool

    has_previous: bool
