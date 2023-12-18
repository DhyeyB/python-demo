from datetime import datetime
from typing import Any
from app import db
from app.helpers.constants import UserType
from app.helpers.constants import SortingOrder
from app.models.account import Account
from app.models.base import Base
from app.models.user import User
from sqlalchemy import ForeignKey
from sqlalchemy import or_
from sqlalchemy import asc, desc
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import backref


class UserInvite(Base):
    __tablename__ = 'user_invite'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    user_invited_by = db.Column(
        db.String, db.ForeignKey(User.uuid), nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship('Account', backref=backref('user_invite', passive_deletes=True))

    # Define a unique constraint for account_uuid and email combination
    __table_args__ = (UniqueConstraint(  # type: ignore  # noqa: FKA100
        'account_uuid', 'email', name='unique_account_email'),)

    def update_status(self, status):
        """Update user invite status"""
        self.status = status
        db.session.commit()

    @classmethod
    def get_user_invite_list_by_account(cls, q: Any = None, sort: Any = None, page: Any = None, size: Any = None,
                                        account_uuid: str = account_uuid) -> tuple:
        """
        Get all records belong to given account_uuid. Then
        Filters records based on search(q) and sorts them based on page, size, sort(sorting parameter).
        """
        query = db.session.query(cls).filter(cls.account_uuid == account_uuid)

        if sort == SortingOrder.ASC.value:
            query = query.order_by(asc(cls.created_at))
        else:
            query = query.order_by(desc(cls.created_at))

        if q:
            query = query.filter(
                or_(cls.first_name.ilike('%{}%'.format(q)),  # type: ignore  # noqa: FKA100
                    cls.last_name.ilike('%{}%'.format(q)),
                    cls.email.ilike('%{}%'.format(q)),
                    cls.status.ilike('%{}%'.format(q)))
            )

        query_count = query.count()

        if page and size:
            offset = (int(page) - 1) * int(size)
            query = query.limit(int(size))
            query = query.offset(offset)

        return query.all(), query_count

    @classmethod
    def get_invited_user_count_by_account(cls, account_uuid: str):
        """Return total user in that account"""
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).count()

    @classmethod
    def serialize(cls, details: Any) -> list:
        """ Make a list of dictionary from objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            single_data_obj = {
                'id': single_data.id,
                'uuid': single_data.uuid,
                'user_invited_by': single_data.user_invited_by,
                'account_uuid': single_data.account_uuid,
                'first_name': single_data.first_name,
                'last_name': single_data.last_name,
                'email': single_data.email,
                'status': single_data.status,
                'user_type': UserType.SECONDARY_USER.value,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }

            data.append(single_data_obj)
        return data
