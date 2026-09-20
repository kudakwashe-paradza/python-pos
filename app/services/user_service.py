from repositories.user_repository import user_repository
from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from schemas.user import UserCreate,UserUpdate
from core.security import hash_password

def get_user(db:Session,id:int):
    user=user_repository.get(db,id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not Found")
    return user

def list_users(db:Session):
    return user_repository.get_all(db)

def create_user(db:Session,data:UserCreate):
    payload=data.model_dump()
    plain_password=payload.pop("password")
    payload["password_hash"]=hash_password(plain_password)
    return user_repository.create(db,payload)

def update_user(db:Session,user_id:int,data:UserUpdate):
    user=get_user(db,user_id)
    return user_repository.update(db,user,data.model_dump(exclude_unset=True))

def delete_user(db:Session,user_id:int):
    user=get_user(db,user_id)
    user_repository.delete(db,user)
        
    