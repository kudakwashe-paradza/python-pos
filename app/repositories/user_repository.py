from models.user import User
from sqlalchemy.orm import Session
from repositories.base import BaseRepository

class UserRepository:
    def __init__(self):
        self.__model=User

    def get_by_user_name(self,db:Session,user_name:str):
        return db.get(User).filter(User.user_name).first()  

    def get_by_id(self,db:Session,id:int,user_id:int):
            return db.query(User).filter(User.user_id==user_id).first()
    
    def get_all(self,db:Session):
        return db.query(User).all()

    def create(self,db:Session,data:dict):
        user = User(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, db_obj: User, data: dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: User):
        db.delete(db_obj)
        db.commit()


user_repository = UserRepository()