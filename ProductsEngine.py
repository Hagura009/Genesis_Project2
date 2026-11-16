from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, Session, select
from database import get_session

# Inicialização do FastAPI (mantendo o nome 'products' como no seu exemplo)
products = FastAPI(
    title="Products API",
    description="API for managing products",
)

# --- MODELOS ---

class ProductBase(SQLModel):
    name: str
    description: str
    price: float
    category: str = Field(default="undefined")

class Product(ProductBase, table=True):
    __tablename__ = "products"
    id: Optional[int] = Field(default=None, primary_key=True)

class CreateProduct(ProductBase):
    pass

class ProductView(ProductBase):
    id: int

class UpdateProduct(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None


# --- ROTAS (ENDPOINTS) ---

@products.post("/products/", response_model=ProductView, status_code=status.HTTP_201_CREATED)
def create_product(product_in: CreateProduct, session: Session = Depends(get_session)):
    db_product = Product.model_validate(product_in)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@products.get("/products/", response_model=List[ProductView])
def list_products(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None, 
    session: Session = Depends(get_session)
):
    query = select(Product)
    if category:
        query = query.where(Product.category == category)
    
    db_products = session.exec(query.offset(skip).limit(limit)).all()
    return db_products


@products.get("/products/{product_id}", response_model=ProductView)
def get_product(product_id: int, session: Session = Depends(get_session)):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found"
        )
    return db_product


@products.patch("/products/{product_id}", response_model=ProductView)
def update_product(
    product_id: int, 
    product_in: UpdateProduct, 
    session: Session = Depends(get_session)
):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found"
        )
    
    product_data = product_in.model_dump(exclude_unset=True)
    for key, value in product_data.items():
        setattr(db_product, key, value)
        
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@products.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, session: Session = Depends(get_session)):
    """Deleta um produto pelo ID."""
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found"
        )
    
    session.delete(db_product)
    session.commit()
    return None
    