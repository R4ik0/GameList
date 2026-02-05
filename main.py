import time
from fastapi import FastAPI, Depends, Request
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, REGISTRY

from src.routers import auth_router, igdb_router, user_router
from dependencies import get_current_user
import uvicorn

from dotenv import load_dotenv
load_dotenv()

from metrics import REQUEST_COUNT, REQUEST_LATENCY
from push_metrics import push_metrics

app = FastAPI(title="GameList API", version="1.0.0")

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    print("\n[PROM] Middleware called")

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    endpoint = request.url.path

    print(f"[PROM] {request.method} {endpoint} -> {response.status_code}")
    print(f"[PROM] Duration: {duration:.4f}s")

    try:
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)

        print("[PROM] Metrics updated")
    except Exception as e:
        print("[PROM] Metrics update error:", repr(e))

    try:
        push_metrics()
        print("[PROM] Metrics pushed to Grafana Cloud")
    except Exception as e:
        print("[PROM] Metrics push failed")
        print("[PROM] Reason:", repr(e))

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(igdb_router.router)
app.include_router(user_router.router)

@app.get("/")
async def root():
    return {"message": "API ready. Use /docs for interactive docs."}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), media_type="text/plain")