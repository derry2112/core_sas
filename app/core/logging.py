import functools
import inspect
import os
import time
from logging import Formatter, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler
from typing import Callable

from dotenv import load_dotenv
from fastapi import Request
from tortoise.backends.asyncpg.client import AsyncpgDBClient

load_dotenv()

DEFAULT_SLOW_THRESHOLD = 1.0

ROUTER_SLOW_THRESHOLDS = {
    "/admin": 0.3,
}

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

log_dir = "/var/log/fastapi"
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "app.log")

# ===============================
# Root Logger (file + stdout)
# ===============================
formatter = Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
handler.setFormatter(formatter)

logger = getLogger("app")
logger.setLevel(LOG_LEVEL)
logger.addHandler(handler)

stream_handler = StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# ===============================
# Console-only logger (tidak di-OTel)
# ===============================
console_logger = getLogger("console-only")
console_handler = StreamHandler()
console_handler.setFormatter(Formatter("%(asctime)s [CONSOLE] %(message)s"))
console_logger.addHandler(console_handler)
console_logger.setLevel("INFO")


# ===============================
# DB Logging
# ===============================
class LoggingDBClient(AsyncpgDBClient):
    async def execute_query(self, query: str, *args, **kwargs):
        start_time = time.time()
        result = await super().execute_query(query, *args, **kwargs)
        duration = time.time() - start_time

        if duration > DEFAULT_SLOW_THRESHOLD:
            logger.warning("SLOW SQL: %s | duration=%.3fs", query, duration)
        # else:
        #     logger.info("SQL QUERY: %s | duration=%.3fs", query, duration)

        return result

    async def close(self):
        # panggil close bawaan jika ada
        if hasattr(super(), "close"):
            await super().close()
        else:
            # jika tidak ada close bawaan, cukup pass
            pass


# ===============================
# Utility Decorators
# ===============================
def log_slow_call(label: str, threshold: float = 1.0):
    def decorator(func: Callable):
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.time()
                result = await func(*args, **kwargs)
                duration = time.time() - start
                if duration > threshold:
                    logger.warning(
                        "SLOW %s: %s took %.3fs", label.upper(), func.__name__, duration
                    )
                return result

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start
                if duration > threshold:
                    logger.warning(
                        "SLOW %s: %s took %.3fs", label.upper(), func.__name__, duration
                    )
                return result

            return sync_wrapper

    return decorator


def log_if_slow(start_time: float, label: str, threshold: float = 0.5):
    duration = time.time() - start_time
    if duration > threshold:
        logger.warning(f"SLOW {label.upper()}: took {duration:.3f}s")


# ===============================
# Middleware untuk slow request
# ===============================
async def slow_request_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    threshold = DEFAULT_SLOW_THRESHOLD
    for prefix, t in ROUTER_SLOW_THRESHOLDS.items():
        if request.url.path.startswith(prefix):
            threshold = t
            break

    if duration > threshold:
        logger.warning(
            "SLOW REQUEST [%.2fs]: %s %s took %.3fs",
            threshold,
            request.method,
            request.url.path,
            duration,
        )

    return response


# import functools
# import inspect
# import os
# import time
# from logging import Formatter, StreamHandler, getLogger
# from logging.handlers import RotatingFileHandler
# from typing import Callable

# from dotenv import load_dotenv
# from fastapi import Request
# from tortoise.backends.base.client import BaseDBAsyncClient

# load_dotenv()

# DEFAULT_SLOW_THRESHOLD = 1.0

# ROUTER_SLOW_THRESHOLDS = {
#     "/admin": 0.3,
# }

# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# log_dir = "/var/log/fastapi"
# os.makedirs(log_dir, exist_ok=True)

# log_file_path = os.path.join(log_dir, "app.log")

# handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
# formatter = Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
# handler.setFormatter(formatter)

# logger = getLogger()

# logger.setLevel(LOG_LEVEL)
# logger.addHandler(handler)
# stream_handler = StreamHandler()
# stream_handler.setFormatter(formatter)
# logger.addHandler(stream_handler)


# class LoggingDBClient(BaseDBAsyncClient):
#     async def execute_query(self, query: str, *args, **kwargs):
#         start_time = time.time()
#         result = await super().execute_query(query, *args, **kwargs)
#         duration = time.time() - start_time

#         if duration > DEFAULT_SLOW_THRESHOLD:
#             logger.warning("SLOW SQL: %s | duration=%.3fs", query, duration)
#         else:
#             logger.info("SQL QUERY: %s | duration=%.3fs", query, duration)

#         return result


# def log_slow_call(label: str, threshold: float = 1.0):
#     def decorator(func: Callable):
#         if inspect.iscoroutinefunction(func):

#             @functools.wraps(func)
#             async def async_wrapper(*args, **kwargs):
#                 start = time.time()
#                 result = await func(*args, **kwargs)
#                 duration = time.time() - start
#                 if duration > threshold:
#                     logger.warning(
#                         "SLOW %s: %s took %.3fs", label.upper(), func.__name__, duration
#                     )
#                 return result

#             return async_wrapper
#         else:

#             @functools.wraps(func)
#             def sync_wrapper(*args, **kwargs):
#                 start = time.time()
#                 result = func(*args, **kwargs)
#                 duration = time.time() - start
#                 if duration > threshold:
#                     logger.warning(
#                         "SLOW %s: %s took %.3fs", label.upper(), func.__name__, duration
#                     )
#                 return result

#             return sync_wrapper

#     return decorator


# def log_if_slow(start_time: float, label: str, threshold: float = 0.5):
#     duration = time.time() - start_time
#     if duration > threshold:
#         logger.warning(f"SLOW {label.upper()}: took {duration:.3f}s")


# async def slow_request_logging_middleware(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     duration = time.time() - start_time

#     threshold = DEFAULT_SLOW_THRESHOLD
#     for prefix, t in ROUTER_SLOW_THRESHOLDS.items():
#         if request.url.path.startswith(prefix):
#             threshold = t
#             break

#     if duration > threshold:
#         logger.warning(
#             "SLOW REQUEST [%.2fs]: %s %s took %.3fs",
#             threshold,
#             request.method,
#             request.url.path,
#             duration,
#         )

#     return response
