from datetime import datetime
from typing import Any
from app import db
from app.helpers.constants import UserType
from app.helpers.constants import SortingOrder
from app.models.account import Account
from app.models.base import Base
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import ForeignKey
from sqlalchemy.ext import hybrid
from sqlalchemy.orm import backref
from app import app
from app import config_data


class User(Base):
    __tablename__ = 'user'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    mobile_number = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    force_password_update = db.Column(db.Boolean, nullable=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    signature = db.Column(db.String, nullable=True)
    user_type = db.Column(db.String, nullable=False)
    deactivated_at = db.Column(db.DateTime, server_default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship('Account', backref=backref('user', passive_deletes=True))

    @hybrid.hybrid_property
    def full_name(self) -> str:
        """Return full name."""
        if self.last_name:
            return self.first_name + ' ' + self.last_name
        return self.first_name

    @classmethod
    def get_users_with_account_legal_name(cls, q: Any = None, sort: Any = None, page: Any = None, size: Any = None) -> tuple:
        """Filters records based on search(q) and sorts them based on page, size, sort(sorting parameter)."""
        query = db.session.query(cls.first_name, cls.last_name, cls.email, cls.mobile_number, cls.user_type,
                                 Account.legal_name).join(Account, cls.account_uuid == Account.uuid).filter(
            cls.user_type != UserType.SUPER_ADMIN.value)

        if sort == SortingOrder.ASC.value:
            query = query.order_by(asc(cls.created_at))
        else:
            query = query.order_by(desc(cls.created_at))

        if q:
            query = query.filter(
                or_(cls.first_name.ilike('%{}%'.format(q)),  # type: ignore  # noqa: FKA100
                    cls.last_name.ilike('%{}%'.format(q)),
                    cls.email.ilike('%{}%'.format(q)),
                    cls.mobile_number.ilike('%{}%'.format(q)),
                    cls.user_type.ilike('%{}%'.format(q)),
                    Account.legal_name
                    )
            )
        query_count = query.count()

        if page and size:
            offset = (int(page) - 1) * int(size)
            query = query.limit(int(size))
            query = query.offset(offset)

        return query.all(), query_count

    @classmethod
    def get_all_user_detail(cls) -> dict:
        """Return all records with basic details from user table."""
        query = db.session.query(
            cls.id, cls.first_name, cls.full_name, cls.last_name, cls.email).all()
        return {r.id: r._asdict() for r in query}

    @classmethod
    def get_by_email(cls, email: str) -> Any:
        """Filter records by email."""
        return db.session.query(cls).filter(cls.email == email).first()

    @classmethod
    def is_user_with_account_id(cls, user_uuid: str, account_uuid: str) -> Any:
        """Check if the user exist with this account id."""
        return db.session.query(cls).filter(and_(cls.account_uuid == account_uuid, cls.uuid == user_uuid)).first()

    @classmethod
    def get_primary_user_of_account(cls, account_uuid: str):
        """Return Account owner - primary user of account"""
        if config_data.get('TESTING'):
            return db.session.query(cls).filter(
                and_(cls.account_uuid == account_uuid, cls.user_type == UserType.PRIMARY_USER.value)).first()
        with app.app_context():
            return db.session.query(cls).filter(
                and_(cls.account_uuid == account_uuid, cls.user_type == UserType.PRIMARY_USER.value)).first()

    @classmethod
    def get_user_count_by_account(cls, account_uuid: str):
        """Return total user in that account"""
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).count()
    
    @classmethod
    def get_all_user_by_account_uuid(cls, account_uuid: str):
        """Return total user in that account"""
        with app.app_context():
            return db.session.query(cls).filter(cls.account_uuid == account_uuid).all()

    @classmethod
    def serialize(cls, details: Any, single_object: bool = False) -> Any:
        """ Make a list of User objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            single_data_obj = {
                'id': single_data.id,
                'uuid': single_data.uuid,
                'account_uuid': single_data.account_uuid,
                'first_name': single_data.first_name,
                'last_name': single_data.last_name,
                'email': single_data.email,
                'force_password_update': single_data.force_password_update,
                'email_verified_at': single_data.email_verified_at,
                'mobile_number': single_data.mobile_number,
                'signature': single_data.signature,
                'user_type': single_data.user_type,
                'deactivated_at': single_data.deactivated_at,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }

            data.append(single_data_obj)
        if single_object:
            # If single_object is True, return the first item as a single object
            return data[0] if data else None
        else:
            return data
