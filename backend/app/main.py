from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .config import settings
from .routers import auth, lost_items, found_items, iot, matches, claims, analytics

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AKTU Mini Project: AI + IoT Smart Lost & Found Campus Platform",
    version=settings.VERSION
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(lost_items.router, prefix=settings.API_PREFIX)
app.include_router(found_items.router, prefix=settings.API_PREFIX)
app.include_router(iot.router, prefix=settings.API_PREFIX)
app.include_router(matches.router, prefix=settings.API_PREFIX)
app.include_router(claims.router, prefix=settings.API_PREFIX)
app.include_router(analytics.router, prefix=settings.API_PREFIX)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI + IoT Smart Lost & Found System API Running. UI not found in static directory."}

@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "system": settings.PROJECT_NAME, "version": settings.VERSION}
