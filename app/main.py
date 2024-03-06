from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .backend.config import settings
from .routers import auth, health, users

router_prefix = settings.base_url_suffix

app = FastAPI()

origins = settings.cors_allowed_origins or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=router_prefix)
app.include_router(auth.router, prefix=router_prefix)
app.include_router(users.router, prefix=router_prefix)
