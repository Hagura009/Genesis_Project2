from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel

from database import engine
from products import Product, router as products_router
from users import Account, router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Génesis API",
    description="API unificada de usuarios y productos",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"message": "Génesis API running"}


app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(products_router, prefix="/products", tags=["Products"])