from datetime import datetime
from typing import Any
from app import db
from app.models.account import Account
from app.models.base import Base
from sqlalchemy import ForeignKey
from app.helpers.constants import SortingOrder
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import or_
from sqlalchemy.orm import backref


class Folder(Base):
    __tablename__ = 'folder'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    folder_name = db.Column(db.String, nullable=False)
    folder_name_slug = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship('Account', backref=backref('folder', passive_deletes=True))

    @classmethod
    def check_if_folder_exist(cls, account_uuid: str, folder_name_slug: str, folder_uuid: str = ''):
        """
        Check if folder with given name already exists.

        If folder_uuid: [Used in case of update folder API]
            check if client with given slug already exists except given client.
        """
        if folder_uuid:
            return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(
                cls.folder_name_slug == folder_name_slug).filter(cls.uuid != folder_uuid).first() is not None

        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(cls.folder_name_slug == folder_name_slug).first() is not None

    @classmethod
    def get_folder_list(cls, account_uuid: str, q: Any = None, sort: Any = None, page: Any = None, size: Any = None) -> tuple:
        """Filters records based on search(q) and sorts them based on page, size, sort(sorting parameter)."""
        query = db.session.query(cls).filter(cls.account_uuid == account_uuid)

        if sort == SortingOrder.ASC.value:
            query = query.order_by(asc(cls.created_at))
        else:
            query = query.order_by(desc(cls.created_at))

        if q:
            query = query.filter(
                or_(cls.folder_name.ilike('%{}%'.format(q)))  # type: ignore  # noqa: FKA100
            )

        query_count = query.count()

        if page and size:
            offset = (int(page) - 1) * int(size)
            query = query.limit(int(size))
            query = query.offset(offset)

        return query.all(), query_count

    @classmethod
    def serialize(cls, details: Any) -> Any:
        """ Make a list of Client objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            single_data_obj = {
                'id': single_data.id,
                'uuid': single_data.uuid,
                'account_uuid': single_data.account_uuid,
                'folder_name': single_data.folder_name,
                'folder_name_slug': single_data.folder_name_slug,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }

            data.append(single_data_obj)

        return data
