from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.menu import (
    Category, CategoryCreate, CategoryUpdate, 
    Product, ProductCreate, ProductUpdate,
    ProductOption, ProductOptionCreate, ProductOptionUpdate,
    ProductVariant, ProductVariantCreate, ProductVariantUpdate
)
from app.models.menu import Category as CategoryModel, Product as ProductModel
from app.models.menu import ProductOption as ProductOptionModel, ProductVariant as ProductVariantModel

router = APIRouter()


@router.get("/categories", response_model=List[Category])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all categories"""
    result = await db.execute(
        CategoryModel.__table__.select()
        .where(CategoryModel.is_active == True)
        .order_by(CategoryModel.position)
        .offset(skip)
        .limit(limit)
    )
    categories = result.fetchall()
    return [Category.from_orm(row) for row in categories]


@router.get("/categories/{category_id}", response_model=Category)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific category by ID"""
    result = await db.execute(
        CategoryModel.__table__.select()
        .where(CategoryModel.id == category_id)
    )
    category = result.fetchone()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return Category.from_orm(category)


@router.post("/categories", response_model=Category)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new category"""
    db_category = CategoryModel(**category.dict())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return Category.from_orm(db_category)


@router.put("/categories/{category_id}", response_model=Category)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a category"""
    result = await db.execute(
        CategoryModel.__table__.select()
        .where(CategoryModel.id == category_id)
    )
    db_category = result.fetchone()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_update.dict(exclude_unset=True)
    await db.execute(
        CategoryModel.__table__.update()
        .where(CategoryModel.id == category_id)
        .values(**update_data)
    )
    await db.commit()
    
    result = await db.execute(
        CategoryModel.__table__.select()
        .where(CategoryModel.id == category_id)
    )
    updated_category = result.fetchone()
    return Category.from_orm(updated_category)


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a category (soft delete by setting is_active to False)"""
    result = await db.execute(
        CategoryModel.__table__.select()
        .where(CategoryModel.id == category_id)
    )
    db_category = result.fetchone()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await db.execute(
        CategoryModel.__table__.update()
        .where(CategoryModel.id == category_id)
        .values(is_active=False)
    )
    await db.commit()
    return {"message": "Category deleted successfully"}


@router.get("/products", response_model=List[Product])
async def get_products(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category_id: int = None,
    is_active: bool = True
):
    """Get all products"""
    query = ProductModel.__table__.select().where(ProductModel.is_active == is_active)
    
    if category_id:
        query = query.where(ProductModel.category_id == category_id)
    
    query = query.order_by(ProductModel.position).offset(skip).limit(limit)
    
    result = await db.execute(query)
    products = result.fetchall()
    return [Product.from_orm(row) for row in products]


@router.get("/products/{product_id}", response_model=Product)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific product by ID"""
    result = await db.execute(
        ProductModel.__table__.select()
        .where(ProductModel.id == product_id)
    )
    product = result.fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product.from_orm(product)


@router.post("/products", response_model=Product)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new product"""
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return Product.from_orm(db_product)


@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a product"""
    result = await db.execute(
        ProductModel.__table__.select()
        .where(ProductModel.id == product_id)
    )
    db_product = result.fetchone()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    await db.execute(
        ProductModel.__table__.update()
        .where(ProductModel.id == product_id)
        .values(**update_data)
    )
    await db.commit()
    
    result = await db.execute(
        ProductModel.__table__.select()
        .where(ProductModel.id == product_id)
    )
    updated_product = result.fetchone()
    return Product.from_orm(updated_product)


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a product (soft delete by setting is_active to False)"""
    result = await db.execute(
        ProductModel.__table__.select()
        .where(ProductModel.id == product_id)
    )
    db_product = result.fetchone()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.execute(
        ProductModel.__table__.update()
        .where(ProductModel.id == product_id)
        .values(is_active=False)
    )
    await db.commit()
    return {"message": "Product deleted successfully"}


@router.get("/products/{product_id}/options", response_model=List[ProductOption])
async def get_product_options(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all options for a product"""
    result = await db.execute(
        ProductOptionModel.__table__.select()
        .where(ProductOptionModel.product_id == product_id)
        .where(ProductOptionModel.is_active == True)
        .order_by(ProductOptionModel.position)
    )
    options = result.fetchall()
    return [ProductOption.from_orm(row) for row in options]


@router.post("/products/{product_id}/options", response_model=ProductOption)
async def create_product_option(
    product_id: int,
    option: ProductOptionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new product option"""
    option_data = option.dict()
    option_data["product_id"] = product_id
    db_option = ProductOptionModel(**option_data)
    db.add(db_option)
    await db.commit()
    await db.refresh(db_option)
    return ProductOption.from_orm(db_option)


@router.get("/products/{product_id}/variants", response_model=List[ProductVariant])
async def get_product_variants(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all variants for a product"""
    result = await db.execute(
        ProductVariantModel.__table__.select()
        .where(ProductVariantModel.product_id == product_id)
        .where(ProductVariantModel.is_active == True)
        .order_by(ProductVariantModel.position)
    )
    variants = result.fetchall()
    return [ProductVariant.from_orm(row) for row in variants]


@router.post("/products/{product_id}/variants", response_model=ProductVariant)
async def create_product_variant(
    product_id: int,
    variant: ProductVariantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new product variant"""
    variant_data = variant.dict()
    variant_data["product_id"] = product_id
    db_variant = ProductVariantModel(**variant_data)
    db.add(db_variant)
    await db.commit()
    await db.refresh(db_variant)
    return ProductVariant.from_orm(db_variant)