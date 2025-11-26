import datetime
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi_limiter import FastAPILimiter

# === OpenTelemetry ===
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import Resource

# from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# === Prometheus Instrumentator ===
from prometheus_fastapi_instrumentator import Instrumentator
from tortoise import Tortoise

from app.api.crypto.cryptoRouter import router as crypto_router
from app.api.gateway.absensi.absensiRouter import router as absensi_router
from app.api.gateway.dasata.dasataRouter import router as dasata_router
from app.api.gateway.direct.directRouter import router as direct_router
from app.api.gateway.employee.employeeRouter import router as employee_router
from app.api.gateway.files.filesRouter import router as files_router
from app.api.gateway.notification.notifRouter import router as notif_router
from app.api.gateway.personalia.personaliaRouter import router as personalia_router
from app.api.gateway.sarpras.sarprasRouter import router as sarpras_router
from app.api.gateway.tiket.tiketRouter import router as tiket_router
from app.api.users.userRouter import router as users_router
from app.core.config import init_db
from app.core.limiting import rate_limit_dependency
from app.core.logging import logger, slow_request_logging_middleware

# from app.core.rabbitmq import get_rabbit_connection
from app.core.redis import redis_client
from app.services.limiter import RateLimitMiddleware
from app.services.middleware import setup_cors

resource = Resource.create(
    {
        "service.name": "core-service",
        "deployment.environment": "development",
    }
)

provider = TracerProvider(resource=resource)
# trace.set_tracer_provider(TracerProvider(resource=resource))
trace.set_tracer_provider(provider)
tracer_provider = trace.get_tracer_provider()

otlp_exporter = OTLPSpanExporter(endpoint="192.168.2.138:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
LoggingInstrumentor().instrument()
RedisInstrumentor().instrument()
HTTPXClientInstrumentor().instrument()


async def lifespan(app: FastAPI):
    try:
        await FastAPILimiter.init(redis_client)
        logger.info("FastAPI Limiter initialized with Redis.")

        await init_db()
        logger.info("Database initialized.")

        # app.state.rabbit_connection = await get_rabbit_connection()
        # logger.info("RabbitMQ connection established.")

        error_routes = []
        for route in app.routes:
            if isinstance(route, APIRoute):
                try:
                    _ = route.dependant
                except Exception as e:
                    error_routes.append((route.path, str(e)))

        if error_routes:
            logger.error("Error detected on router during startup:")
            for path, err in error_routes:
                logger.error(f"Route: {path} -> Error: {err}")
        else:
            logger.info("All routes validated without error.")

        yield

    except Exception as e:
        logger.error("Error during application startup: %s", str(e))
        raise

    finally:
        await FastAPILimiter.close()
        await Tortoise.close_connections()
        # if hasattr(app.state, "rabbit_connection") and app.state.rabbit_connection:
            # await app.state.rabbit_connection.close()
        logger.info("Connections closed.")


app = FastAPI(lifespan=lifespan, redoc_url=None)
Instrumentator().instrument(app).expose(app)

MAX_UPLOAD_SIZE = 10 * 1024 * 1024

setup_cors(app)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and CI/CD pipeline verification.
    Returns status information about the application and its dependencies.
    """
    # Initialize health status
    health_status = {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": str(datetime.datetime.now(tz=datetime.timezone.utc)),
        "services": {},
    }

    # Check database connection
    try:
        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")
        health_status["services"]["database"] = "connected"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis connection
    try:
        await redis_client.ping()
        health_status["services"]["redis"] = "connected"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check RabbitMQ connection
    # try:
        # if hasattr(app.state, "rabbit_connection") and app.state.rabbit_connection:
        #     if app.state.rabbit_connection.is_closed:
        #         health_status["services"]["rabbitmq"] = "disconnected"
        #         health_status["status"] = "degraded"
        #     else:
        #         health_status["services"]["rabbitmq"] = "connected"
        # else:
        #     health_status["services"]["rabbitmq"] = "not initialized"
        #     health_status["status"] = "degraded"
    except Exception:
        # health_status["services"]["rabbitmq"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


@app.middleware("http")
async def add_coop_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in ("/metrics", "/health"):
        return await call_next(request)

    try:
        await rate_limit_dependency(request)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    return await call_next(request)


@app.middleware("http")
async def block_connect_method(request: Request, call_next):
    if request.method == "CONNECT":
        return JSONResponse(status_code=405, content="Method Not Allowed")
    return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    tracer = trace.get_tracer(__name__)
    start_time = time.time()

    with tracer.start_as_current_span("http_request") as span:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("http.status_code", response.status_code)
        span.set_attribute("http.process_time_ms", process_time)

        ignore_paths = ("/docs", "/openapi.json", "/redoc")
        if not any(request.url.path.startswith(path) for path in ignore_paths):
            msg = (
                f"{request.url.path}"
                # f"{request.method} {request.url.path} "
                f"-> {response.status_code} "
                # f"in {process_time:.2f}ms"
            )
            logger.info(msg)

        return response


@app.get("/trace-test")
async def trace_test():
    tracer = trace.get_tracer(__name__)  # ambil tracer
    with tracer.start_as_current_span("manual-test-span") as span:
        time.sleep(0.05)
        span.set_attribute("example", "yes")
    return {"message": "Trace sent!"}


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    if request.method == "POST" and request.headers.get("Content-Length"):
        content_length = int(request.headers["Content-Length"])
        if content_length > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File is too large")
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled Exception at %s %s: %s", request.method, request.url.path, exc
    )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# Tambahkan logging slow requests
app.middleware("http")(slow_request_logging_middleware)
app.add_middleware(OpenTelemetryMiddleware)
# === Instrument FastAPI ===
FastAPIInstrumentor.instrument_app(app)


app.add_middleware(RateLimitMiddleware, redis=redis_client, rate_limit=10, period=60)

app.include_router(employee_router, prefix="/employee", tags=["API Employee"])
app.include_router(dasata_router, prefix="/dasata", tags=["API Dasata"])
app.include_router(direct_router, prefix="/direct", tags=["API Direct"])
app.include_router(notif_router, prefix="/notif", tags=["API Notification"])
app.include_router(files_router, prefix="/file", tags=["API Files"])
app.include_router(tiket_router, prefix="/tiket", tags=["API Tiketing"])
app.include_router(absensi_router, prefix="/absensi", tags=["API Absensi"])
app.include_router(sarpras_router, prefix="/sarpras", tags=["API Sarpras"])
app.include_router(personalia_router, prefix="/personalia", tags=["API Personalia"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(crypto_router, prefix="/crypto", tags=["Cryptography"])
