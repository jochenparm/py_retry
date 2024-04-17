import functools
import logging
from typing import Callable


def decorator(caller: Callable):
    """Turns caller into a decorator.
    Unlike decorator module, function signature is not preserved.

    :param caller: caller(f, *args, **kwargs)
    """

    def decor(f: Callable):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return caller(f, *args, **kwargs)

        return wrapper

    return decor


class NullHandler(logging.Handler):
    """
    A custom logging handler that does nothing when emitting log records.

    This class represents a logging handler that inherits from `logging.Handler`.
    The `emit` method is overridden to perform no action,
    effectively discarding log records.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        This method simply discards the provied log record and does nothing.

        :returns: None
        """
