"""Contains some basic definitions that can be extended by other models."""
from uuid import uuid4
from typing import Any, Union
from app import db
from app import logger
from sqlalchemy import insert
from datetime import datetime
from app import app
from app import config_data


class Base(db.Model):
    """Base modal for all other modal that contains some basic methods that can be extended by other modals."""
    __abstract__ = True

    @classmethod
    def create_uuid(cls) -> Any:
        """creates a random uuid and checks if exists in the cls table:
        if yes then it recursively calls itself if not the returns the uuid."""
        if config_data.get('TESTING'):
            uuid = str(uuid4())
            exists = db.session.query(cls).filter(cls.uuid == uuid).first()
            if exists:
                cls.create_uuid()
            else:
                return uuid
        else:
            with app.app_context():
                uuid = str(uuid4())
                exists = db.session.query(cls).filter(cls.uuid == uuid).first()
                if exists:
                    cls.create_uuid()
                else:
                    return uuid

    @classmethod
    def bulk_insert(cls, data_list: list) -> None:
        stmt = insert(cls).values(data_list)
        db.session.execute(stmt)
        db.session.commit()

    @classmethod
    def get_by_id(cls, obj_id: int) -> Any:
        """Filter record by id."""
        return db.session.query(cls).filter(cls.id == obj_id).first()

    @classmethod
    def get_by_uuid(cls, uuid: str) -> Any:
        """Filter record by uuid. """
        return db.session.query(cls).filter(cls.uuid == uuid).first()

    @classmethod
    def get_all(cls) -> list:
        """Return  all records of that table"""
        return db.session.query(cls).all()

    @classmethod
    def add(cls, data: dict) -> Any:
        """Method to add DB record."""
        if config_data.get('TESTING'):
            try:
                obj = cls(**data)
                db.session.add(obj)
                db.session.commit()
                return obj
            except Exception as error:
                logger.error('error while creating record for {} table : {}'.format(
                    cls.__name__, error))
        else:
            with app.app_context():
                try:
                    obj = cls(**data)
                    db.session.add(obj)
                    db.session.commit()
                    return obj
                except Exception as error:
                    logger.error('error while creating record for {} table : {}'.format(
                        cls.__name__, error))

    @classmethod
    def update(cls):
        """ Method to update DB record."""
        db.session.commit()

    @classmethod
    def delete_by_id(cls, obj_id: int) -> Any:
        """Delink records by id ."""
        db.session.query(cls).filter(cls.id == obj_id).delete()

    @classmethod
    def delete_by_uuid(cls, uuid: str) -> Any:
        """Delink records by uuid ."""
        with app.app_context():
            db.session.query(cls).filter(cls.uuid == uuid).delete()

            logger.info(f'Account with uuid: {uuid} is deleted from db')

    @classmethod
    def get_total_count(cls, start_timestamp: Union[int, None] = None, end_timestamp: Union[int, None] = None):
        """Get total records of that table ."""
        query = db.session.query(cls)
        if start_timestamp is not None:
            start_date = datetime.utcfromtimestamp(start_timestamp)
            query = query.filter(cls.created_at >= start_date)

        if end_timestamp is not None:
            end_date = datetime.utcfromtimestamp(end_timestamp)
            query = query.filter(cls.created_at <= end_date)

        # Perform the count on the filtered query
        count = query.count()
        return count
