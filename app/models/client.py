from datetime import datetime
from typing import Any
from app import db
from app.helpers.constants import SortingOrder
from app.models.account import Account
from app.models.base import Base
from app.models.user import User
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import ForeignKey
from sqlalchemy import or_
from sqlalchemy.orm import backref


class Client(Base):
    __tablename__ = 'client'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    created_by = db.Column(db.String, ForeignKey(User.uuid), nullable=False)
    legal_name = db.Column(db.String, nullable=False)
    legal_name_slug = db.Column(db.String, nullable=False)
    display_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    street_name = db.Column(db.String)
    postal_code = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    country = db.Column(db.String)
    priority_required = db.Column(
        db.Boolean, default=False, server_default='f', nullable=False)
    is_account_client = db.Column(
        db.Boolean, default=False, server_default='f', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship(
        'Account', backref=backref('client', passive_deletes=True))

    @classmethod
    def get_all_by_account_uuid(cls, q: Any = None, sort: Any = None, page: Any = None, size: Any = None,
                                account_uuid: str = account_uuid) -> tuple:
        """
        Get all records belong to given account_uuid. Then
        Filter records based on search(q) and sorts them based on page, size, sort(sorting parameter).
        """
        query = db.session.query(cls).filter(
            cls.account_uuid == account_uuid).filter(cls.is_account_client == False)  # type: ignore  # noqa: E712

        if sort == SortingOrder.ASC.value:
            query = query.order_by(asc(cls.created_at))
        else:
            query = query.order_by(desc(cls.created_at))

        if q:
            query = query.filter(
                or_(cls.legal_name.ilike('%{}%'.format(q)),  # type: ignore  # noqa: FKA100
                    cls.display_name.ilike('%{}%'.format(q)),
                    cls.email.ilike('%{}%'.format(q)),
                    cls.phone.ilike('%{}%'.format(q)),
                    cls.street_name.ilike('%{}%'.format(q)),
                    cls.postal_code.ilike('%{}%'.format(q)),
                    cls.city.ilike('%{}%'.format(q)),
                    cls.state.ilike('%{}%'.format(q)),
                    cls.country.ilike('%{}%'.format(q))
                    )
            )

        query_count = query.count()

        if page and size:
            offset = (int(page) - 1) * int(size)
            query = query.limit(int(size))
            query = query.offset(offset)

        return query.all(), query_count

    @classmethod
    def serialize(cls, details: Any, single_object: bool = False) -> Any:
        """Create a list of dictionaries from objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            single_data_obj = {
                'id': single_data.id,
                'uuid': single_data.uuid,
                'account_uuid': single_data.account_uuid,
                'created_by': single_data.created_by,
                'legal_name': single_data.legal_name,
                'legal_name_slug': single_data.legal_name_slug,
                'display_name': single_data.display_name,
                'email': single_data.email,
                'phone': single_data.phone,
                'street_name': single_data.street_name,
                'postal_code': single_data.postal_code,
                'city': single_data.city,
                'state': single_data.state,
                'country': single_data.country,
                'priority_required': single_data.priority_required,
                'is_account_client': single_data.is_account_client,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }
            data.append(single_data_obj)
        if single_object:
            # If single_object is True, return the first item as a single object
            return data[0] if data else None
        else:
            return data

    @classmethod
    def check_if_client_exits(cls, account_uuid: str, legal_name_slug: str, client_uuid: str = ''):
        """
        Check if client with given slug already exists.

        If client_uuid: [Used in case of update client API]
            check if client with given slug already exists except given client.
        """
        if client_uuid:
            return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(
                cls.legal_name_slug == legal_name_slug).filter(cls.uuid != client_uuid).first() is not None
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(
            cls.legal_name_slug == legal_name_slug).first() is not None

    @classmethod
    def get_by_user_uuid(cls, user_uuid):
        return db.session.query(cls).filter(cls.created_by == user_uuid).filter(cls.is_account_client == False).first()  # type: ignore  # noqa: E712

    @classmethod
    def get_default_account_client(cls, account_uuid):
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(
            cls.is_account_client == True).first()  # type: ignore  # noqa: E712
