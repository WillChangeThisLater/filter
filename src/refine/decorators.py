import asyncio
import functools
import logging
import random

logger = logging.getLogger(__name__)

def retry(max_retries=3, default_return=False, min_delay=1, max_delay=10):
    """
    Decorator to retry a function up to max_retries times
    with a random delay (jiggle) between retries.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__} with error: {e}")
                    if attempt < max_retries - 1:  # No need to delay on final retry
                        jitter = random.uniform(min_delay, max_delay)
                        logger.info(f"Retrying after {jitter:.2f} seconds")
                        await asyncio.sleep(jitter)

            logger.error(f"All {max_retries} attempts failed for {func.__name__}. Returning default: {default_return}")
            return default_return

        return wrapper

    return decorator
