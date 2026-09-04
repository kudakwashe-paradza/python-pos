from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_all(self, db: Session):
        return db.query(self.model).all()

    def get_by_id(self, db: Session, item_id: int):
        return db.query(self.model).filter(self.model.id == item_id).first()

    def create(self, db: Session, data):
        db_item = self.model(**data)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def update(self, db: Session, item_id: int, data):
        db_item = self.get_by_id(db, item_id)

        if not db_item:
            return None

        for key, value in data.items():
            setattr(db_item, key, value)

        db.commit()
        db.refresh(db_item)

        return db_item

    def delete(self, db: Session, item_id: int):
        db_item = self.get_by_id(db, item_id)

        if not db_item:
            return None

        db.delete(db_item)
        db.commit()

        return db_item
