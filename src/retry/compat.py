import logging


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
