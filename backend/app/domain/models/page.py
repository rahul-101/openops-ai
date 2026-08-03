"""
Generic pagination model.
"""

from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Represents a paginated collection."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    items: list[T]

    page: int

    size: int

    total_items: int

    @property
    def total_pages(self) -> int:
        """Return total number of pages."""
        if self.total_items == 0:
            return 0

        return ceil(self.total_items / self.size)

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1
