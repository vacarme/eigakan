from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

EXC_HANDLERS = {
    RateLimitExceeded: _rate_limit_exceeded_handler,
}
