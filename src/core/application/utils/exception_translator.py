from collections.abc import Callable
from functools import wraps


def exc_translator[**FuncP, ResultT](
    reraise: type[Exception],
    skip: tuple[type[Exception], ...] | type[Exception] | None = None,
) -> Callable[[Callable[FuncP, ResultT]], Callable[FuncP, ResultT]]:
    """
    Translate exceptions to a different exception type.

    :param reraise: Exception type to raise.
    :param skip: Exception types to skip.
    """

    def decorator(func: Callable[FuncP, ResultT]) -> Callable[FuncP, ResultT]:
        @wraps(func)
        def wrapper(*args: FuncP.args, **kwargs: FuncP.kwargs) -> ResultT:
            try:
                result = func(*args, **kwargs)

            except Exception as exc:
                if skip and isinstance(exc, skip):
                    raise

                raise reraise() from exc

            return result

        return wrapper

    return decorator
