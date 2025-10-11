from datetime import datetime, timezone
from decimal import Decimal
from traceback import format_exc
from typing import Callable, TypeVar


def utcnow() -> datetime:
    """ UTC datetime (TZ aware) """
    return datetime.now(timezone.utc)


def start_main(main_func, close_func=None):
    """Start main_func and use close_func at exit"""
    try:
        main_func()
    except (SystemExit, KeyboardInterrupt):
        pass
    except Exception:
        from common import log
        log.error(f"Script exit with error:\n{format_exc()}")
    finally:
        if close_func:
            close_func()


def chunks(source: list | tuple, n: int):
    """Yield successive n-sized chunks from source."""
    for i in range(0, len(source), n):
        yield source[i:i + n]


def _d(value_float: float | int) -> Decimal:
    return Decimal('%s' % value_float)




T = TypeVar('T')

def split2list(value: str, sep: str = ';', func: Callable[[str], T] = str) -> list[T]:
    """
    Split to list by separator

    :param value: str
    :param sep: str
    :param func: Callable
    :return: list
    """
    if func == Decimal:
        return [func('%s' % x.strip()) for x in value.split(sep) if x.strip()]
    return [func(x.strip()) for x in value.split(sep) if x.strip()]


def split_in_dict(source_dict, opt_name, sep=';', func: Callable = str):
    """
    Split dict option by separator.

    :param source_dict: dict
    :param opt_name: str
    :param sep: str. E.g. ';'.
    :param func: Callable
    :return: list
    """
    source_dict[opt_name] = split2list(source_dict.get(opt_name, ''), sep, func)


def shorten(text: str | None, char_limit: int) -> str:
    """
    Shorten text:
    (' Hello World ', 11) -> 'Hello World'
    (' Hello World ', 10) -> 'Hello W...'
    """
    if not isinstance(text, str):
        return ''
    text = text.strip()
    if len(text) <= char_limit:
        return text
    return text[:(char_limit - 3)] + '...'
