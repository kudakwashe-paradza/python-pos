from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from services import category_service
from schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return category_service.list_categories(db)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return category_service.get_category(db, category_id)


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return category_service.create_category(db, data)


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    return category_service.update_category(db, category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    return category_service.delete_category(db, category_id)