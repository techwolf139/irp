import asyncio
import functools
from typing import Any, Awaitable, Callable, Optional, TypeVar

T = TypeVar('T')
DecoratorFunc = Callable[..., Awaitable[T]]
DecoratorReturn = Callable[[DecoratorFunc], DecoratorFunc]


def retry_async(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> DecoratorReturn:
    """异步函数重试装饰器。"""
    def decorator(func: DecoratorFunc) -> DecoratorFunc:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception: BaseException | None = None
            
            for attempt in range(max_retries + 1):
                try:
                    result: T = await func(*args, **kwargs)
                    return result
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        break
            
            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Function executed but no result returned")
        
        return wrapper
    return decorator


class RetryConfig:
    """重试配置类。"""
    
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_DELAY = 1.0
    DEFAULT_BACKOFF = 2.0
    DEFAULT_TIMEOUT = 30.0
    
    def __init__(
        self,
        max_retries: Optional[int] = None,
        delay: Optional[float] = None,
        backoff: Optional[float] = None,
        timeout: Optional[float] = None
    ):
        self.max_retries = max_retries or self.DEFAULT_MAX_RETRIES
        self.delay = delay or self.DEFAULT_DELAY
        self.backoff = backoff or self.DEFAULT_BACKOFF
        self.timeout = timeout or self.DEFAULT_TIMEOUT
