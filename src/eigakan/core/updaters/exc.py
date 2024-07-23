"""Custom exceptions for the application."""


class __UpdaterException(Exception):
    """Base class for exceptions in this module."""


class UpdaterNotLoaded(__UpdaterException):
    """Updater not loaded."""

    def __init__(self, updater_name: str, method_name: str) -> None:
        msg = (
            f"{updater_name} must be called "
            f"with a model before accessing '{method_name}'."
        )
        super().__init__(msg)


class __PaginationException(Exception):
    """Base class for exceptions in this module."""


class PaginationInvalidArgument(__PaginationException):
    """Invalid parameter."""

    def __init__(self, parameter: str) -> None:
        msg = f"{parameter} should be greater or equal to 1."
        super().__init__(msg)
