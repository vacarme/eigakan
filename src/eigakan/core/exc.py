"""Custom exceptions for the application."""

from __future__ import annotations


class __CRUDException(Exception):
    """Base class for exceptions in crud module."""


class ResourceNotFound(__CRUDException):
    """Raised when a resource is not found."""

    def __init__(self, column: str = "", value="") -> None:
        msg = (
            f"Resource with '{column} = {value}' not found."
            if column and value
            else "Resource not found."
        )
        super().__init__(msg)


class DuplicatedResource(__CRUDException):
    """Raised when a resource already exists."""

    def __init__(self, column: str = "", value="") -> None:
        msg = (
            f"Resource with '{column} = {value}' already exists."
            if column and value
            else "Resource already exists."
        )
        super().__init__(msg)


class ColumnCannotbeUsedToReadOne(__CRUDException):
    """Raised when a column is not unique."""

    def __init__(self, column: str, model_name: str) -> None:
        msg = (
            f"'{model_name}.{column}' cannot be used to read one resource, "
            "either because it does not exist or is not unique."
        )
        super().__init__(msg)
