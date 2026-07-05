from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.routes import auth, rounds, admin, paystack


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Tony Dynamic API",
    description="Sports betting & lucky number games",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(rounds.router, prefix="/api/rounds", tags=["rounds"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(paystack.router, prefix="/api/paystack", tags=["paystack"])


@app.get("/")
async def root():
    return {"message": "Tony Dynamic API", "status": "online"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
