from typing import Any

from fastapi import HTTPException,status
from sqlalchemy.orm import Session

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
    )

from repositories.user_repository import user_repository
from schemas.user import UserCreate


def register(db:Session,data:UserCreate):
    if user_repository.get_by_user_name(db,data.user_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Username is already taken")

    values=data.model_dump(exclude={"password"})
    values["password_hash"]=hash_password(data.password)
    return user_repository.create(db,values)

def authenicate(db:Session,user_name:str,password:str):
    user=user_repository.get_by_user_name(db,user_name)
    if not user or not verify_password(password,user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate":"Bearer"},
                            )
    return{
        "access_token":create_access_token(user.id),
        "token_type":"bearer",
    }


def get_user_from_token(db:Session,token:str):
    """Validate a JWT and return its active database user"""
    credentials_error=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired toekn",
        headers={"WWW-Authenticate":"Bearer"},
    )
    try:
        payload:dict[str,Any]=decode_access_token(token)
        subject=payload.get("sub")

        if not isinstance(subject,str) or not subject.strip():
            raise credentials_error

        user_id=int(subject)

        if user_id <=0:
            raise credentials_error

    except Exception as e:
        raise credentials_error

    user=user_repository.get_by_id(db,user_id)
    if user is None:
        raise credentials_error

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive,"
        )

    return user
