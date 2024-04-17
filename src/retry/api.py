import logging
import random
import time
from typing import Any, Callable, NewType, Optional, TypedDict, TypeVar, Union

from .compat import decorator

logging_logger = logging.getLogger(__name__)
formatter = "%(asctime)s - %(name)s - L%(lineno)d - %(levelname)s - %(message)s"
logging.basicConfig(format=formatter)


T_Exception = NewType("T_Exception", Exception)
T_I_F = TypeVar("T_I_F", bound=Union[int, float])


class RetryConfig(TypedDict):
    exceptions: Union[T_Exception, tuple[T_Exception, ...]] = Exception
    tries: int = -1
    delay: int = 0
    max_delay: Optional[int] = None
    backoff: int = 1
    jitter: Union[T_I_F, tuple[T_I_F, ...]] = 0
    logger: Optional[logging.Logger] = logging_logger


T_RetryConfig = NewType("T_RetryConfig", RetryConfig)


def __retry_internal(
    f: Callable,
    config: T_RetryConfig,
    f_args: Optional[Any] = None,
    f_kwargs: Optional[Any] = None,
) -> Optional[Callable]:
    """
    Executes a function and retries it if it failed.

    :param f: the function to execute.
    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                    fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                    default: retry.logging_logger. if None, logging is disabled.
    :returns: the result of the f function.
    """
    _delay = config["delay"]
    _tries = config["tries"]

    while _tries > 0:
        try:
            return f(*f_args, **f_kwargs)
        except config["exceptions"] as e:
            _tries -= 1 if _tries > 0 else 0
            if _tries == 0:
                raise

            if config["logger"]:
                config["logger"].warning(f"{e}, retrying in {_delay} seconds...")

            time.sleep(_delay)
            jitter_value = (
                random.uniform(*config["jitter"])
                if isinstance(config["jitter"], tuple)
                else config["jitter"]
            )
            _delay = (
                min(_delay * config["backoff"] + jitter_value, config["max_delay"])
                if config["max_delay"]
                else _delay * config["backoff"] + jitter_value
            )


def retry(
    exceptions: Union[T_Exception, tuple[T_Exception, ...]] = Exception,
    tries: int = -1,
    delay: int = 0,
    max_delay: Optional[int] = None,
    backoff: int = 1,
    jitter: Union[T_I_F, tuple[T_I_F, ...]] = 0,
    logger: Optional[logging.Logger] = logging_logger,
) -> Callable:
    """Returns a retry decorator.

    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                    fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                    default: retry.logging_logger. if None, logging is disabled.
    :returns: a retry decorator.
    """
    config: RetryConfig = {
        "exceptions": exceptions,
        "tries": tries,
        "delay": delay,
        "max_delay": max_delay,
        "backoff": backoff,
        "jitter": (jitter, jitter) if isinstance(jitter, (int, float)) else jitter,
        "logger": logger,
    }

    def retry_decorator(f: Callable):
        @decorator
        def wrapper(*f_args, **f_kwargs):
            return __retry_internal(f, config, f_args, f_kwargs)

        return wrapper

    return retry_decorator


def retry_call(
    f: Callable,
    f_args: Optional[Any] = None,
    f_kwargs: Optional[Any] = None,
    exceptions: Union[T_Exception, tuple[T_Exception, ...]] = Exception,
    tries: int = -1,
    delay: int = 0,
    max_delay: Optional[int] = None,
    backoff: int = 1,
    jitter: Union[T_I_F, tuple[T_I_F, ...]] = 0,
    logger: Optional[logging.Logger] = logging_logger,
) -> Callable:
    """
    Calls a function and re-executes it if it failed.

    :param f: the function to execute.
    :param f_args: the positional arguments of the function to execute.
    :param f_kwargs: the named arguments of the function to execute.
    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                    fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                    default: retry.logging_logger. if None, logging is disabled.
    :returns: the result of the f function.
    """
    config: RetryConfig = {
        "exceptions": exceptions,
        "tries": tries,
        "delay": delay,
        "max_delay": max_delay,
        "backoff": backoff,
        "jitter": (jitter, jitter) if isinstance(jitter, (int, float)) else jitter,
        "logger": logger,
    }
    return __retry_internal(f, config, f_args, f_kwargs)
