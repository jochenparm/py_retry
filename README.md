# PyRetry

A nice decorator tool for retrying tasks when they failed. Forked from [retry](https://github.com/invl/retry) which is not maintained anymore.

## Install

```bash
pip install py-retry
```

## Test cases

```text
╰─± pytest -v
========================================================================== test session starts ==========================================================================
platform darwin -- Python 3.10.12, pytest-6.2.5, py-1.11.0, pluggy-1.0.0 -- /Users/dapeng/.virtualenvs/py310/bin/python
cachedir: .pytest_cache
rootdir: /Users/dapeng/Desktop/code/Git/PyRetry
plugins: anyio-3.7.1
collected 9 items

tests/test_retry.py::test_retry PASSED                                                                                                                            [ 11%]
tests/test_retry.py::test_tries_inf PASSED                                                                                                                        [ 22%]
tests/test_retry.py::test_tries_minus1 PASSED                                                                                                                     [ 33%]
tests/test_retry.py::test_max_delay PASSED                                                                                                                        [ 44%]
tests/test_retry.py::test_fixed_jitter PASSED                                                                                                                     [ 55%]
tests/test_retry.py::test_retry_call PASSED                                                                                                                       [ 66%]
tests/test_retry.py::test_retry_call_2 PASSED                                                                                                                     [ 77%]
tests/test_retry.py::test_retry_call_with_args PASSED                                                                                                             [ 88%]
tests/test_retry.py::test_retry_call_with_kwargs PASSED                                                                                                           [100%]

=========================================================================== 9 passed in 0.10s ===========================================================================
```

## Features

- No external dependency (stdlib only).
- (Optionally) Preserve function signatures (`pip install decorator`).
- Original traceback, easy to debug.

## API

### retry decorator

```python
def retry(exceptions=Exception, tries=-1, delay=0, max_delay=None, backoff=1, jitter=0, logger=logging_logger):
	"""Return a retry decorator.

	:param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
	:param tries: the maximum number of attempts. default: -1 (infinite).
	:param delay: initial delay between attempts. default: 0.
	:param max_delay: the maximum value of delay. default: None (no limit).
	:param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
	:param jitter: extra seconds added to delay between attempts. default: 0.
					fixed if a number, random if a range tuple (min, max)
	:param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
					default: retry.logging_logger. if None, logging is disabled.
	"""
```

Various retrying logic can be achieved by combination of arguments.

### Examples

```python

from retry import retry
```

```python
@retry()
def make_trouble():
	'''Retry until succeed'''
```

```python
@retry(ZeroDivisionError, tries=3, delay=2)
def make_trouble():
	'''Retry on ZeroDivisionError, raise error after 3 attempts, sleep 2 seconds between attempts.'''
```

```python
@retry((ValueError, TypeError), delay=1, backoff=2)
def make_trouble():
	'''Retry on ValueError or TypeError, sleep 1, 2, 4, 8, ... seconds between attempts.'''
```

```python
@retry((ValueError, TypeError), delay=1, backoff=2, max_delay=4)
def make_trouble():
	'''Retry on ValueError or TypeError, sleep 1, 2, 4, 4, ... seconds between attempts.'''
```

```python
@retry(ValueError, delay=1, jitter=1)
def make_trouble():
	'''Retry on ValueError, sleep 1, 2, 3, 4, ... seconds between attempts.'''
```

```python
# If you enable logging, you can get warnings like 'ValueError, retrying in
# 1 seconds'
if __name__ == '__main__':
	import logging
	logging.basicConfig()
	make_trouble()
```

### retry_call

```python
def retry_call(
	f,
	fargs=None,
	fkwargs=None,
	exceptions=Exception,
	tries=-1,
	delay=0,
	max_delay=None,
	backoff=1,
	jitter=0,
	logger=logging_logger
):
	"""
	Calls a function and re-executes it if it failed.

	:param f: the function to execute.
	:param fargs: the positional arguments of the function to execute.
	:param fkwargs: the named arguments of the function to execute.
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
```

This is very similar to the decorator, except that it takes a function and its arguments as parameters. The use case behind it is to be able to dynamically adjust the retry arguments.

```python
import requests

from retry.api import retry_call


def make_trouble(service, info=None):
	if not info:
		info = ''
	r = requests.get(service + info)
	return r.text


def what_is_my_ip(approach=None):
	if approach == "optimistic":
		tries = 1
	elif approach == "conservative":
		tries = 3
	else:
		# skeptical
		tries = -1
	result = retry_call(make_trouble, fargs=["http://ipinfo.io/"], fkwargs={"info": "ip"}, tries=tries)
	print(result)

what_is_my_ip("conservative")
```
