from datetime import datetime
from typing import Any
from app import db
from app.helpers.constants import SortingOrder
from app.models.account import Account
from app.models.base import Base
from sqlalchemy import ForeignKey, asc, desc
from sqlalchemy.orm import backref


class Payment(Base):
    __tablename__ = 'payment'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric)
    status = db.Column(db.String, nullable=False)
    currency = db.Column(db.String, nullable=False)
    reference_payment_id = db.Column(
        db.String(255), nullable=True, unique=True)
    response = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship('Account', backref=backref(
        'payment', passive_deletes=True))

    @classmethod
    def get_by_account(cls, account_uuid: str, q: Any = None, sort: Any = None, page: Any = None,
                       size: Any = None) -> tuple:
        """Filters records based on account, search(q) and sorts them based on page, size, sort(sorting parameter)."""
        query = db.session.query(cls).filter(
            cls.account_uuid == account_uuid)

        if sort == SortingOrder.ASC.value:
            query = query.order_by(asc(cls.created_at))
        else:
            query = query.order_by(desc(cls.created_at))

        if q:
            query = query.filter(cls.status.ilike('%{}%'.format(q)))  # type: ignore  # noqa: FKA100

        query_count = query.count()

        if page and size:
            offset = (int(page) - 1) * int(size)
            query = query.limit(int(size))
            query = query.offset(offset)

        return query.all(), query_count

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
                'amount': single_data.amount,
                'status': single_data.status,
                'currency': single_data.currency,
                'reference_payment_id': single_data.reference_payment_id,
                'response': single_data.response,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }

            data.append(single_data_obj)
        if single_object:
            # If single_object is True, return the first item as a single object
            return data[0] if data else None
        else:
            return data
