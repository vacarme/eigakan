class AuthenticationException(Exception):
    """Base class for exception raised by this package."""


class TokenException(AuthenticationException):
    """An error occured while using the bearer token."""


class TokenValidationException(TokenException):
    """
    Token validation failed.

    Token is validated by the jose package.
    Any failure will raise this exception.
    Most common case would be expired token.

    """


class PasswordException(AuthenticationException):
    """Base class for exception raised by the password module."""


class InvalidPassword(PasswordException):
    """Password does not match the hash stored in db."""

    def __init__(self, msg: str = "Invalid password"):
        super().__init__(msg)
