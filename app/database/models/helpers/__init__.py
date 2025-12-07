from typing import Any

from sqlmodel import SQLModel


class BaseSQLModel(SQLModel):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        # Let SQLModel do its thing, but mypy now knows kwargs are allowed
        super().__init_subclass__(**kwargs)
