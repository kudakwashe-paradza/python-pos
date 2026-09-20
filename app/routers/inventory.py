from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from services import inventory_service
from schemas.inventory import InventoryCreate, InventoryUpdate, InventoryRead
from dependencies import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[InventoryRead])
def list_inventory(db: Session = Depends(get_db)):
    return inventory_service.list_inventory(db)


@router.get("/{inventory_id}", response_model=InventoryRead)
def get_inventory(inventory_id: int, db: Session = Depends(get_db)):
    return inventory_service.get_inventory(db, inventory_id)


@router.post("/", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
def create_inventory(data: InventoryCreate, db: Session = Depends(get_db)):
    return inventory_service.create_inventory(db, data)


@router.put("/{inventory_id}", response_model=InventoryRead)
def update_inventory(inventory_id: int, data: InventoryUpdate, db: Session = Depends(get_db)):
    return inventory_service.update_inventory(db, inventory_id, data)


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory(inventory_id: int, db: Session = Depends(get_db)):
    return inventory_service.delete_inventory(db, inventory_id)