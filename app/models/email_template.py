from datetime import datetime
from typing import Any
from app import db
from app.models.base import Base
from app.models.account import Account
from sqlalchemy import ForeignKey, asc, desc
from app.helpers.constants import SortingOrder
from app import app
from app import config_data
from app.helpers.constants import EmailTypes


class EmailTemplate(Base):
    __tablename__ = 'email_template'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid), nullable=False)
    # email_type :- It's for uniquely get an email template from db for that account.
    email_type = db.Column(db.String, nullable=False)
    email_subject = db.Column(db.String, nullable=False)
    email_body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    @classmethod
    def get_email_template_by_email_type(cls, account_uuid: str, email_type: str):
        if config_data.get('TESTING'):
            return db.session.query(cls).filter(cls.account_uuid == account_uuid, cls.email_type == email_type).first()
        else:
            with app.app_context():
                return db.session.query(cls).filter(cls.account_uuid == account_uuid, cls.email_type == email_type).first()

    @classmethod
    def get_email_template_list(cls, account_uuid: str = account_uuid, q: Any = None, page: Any = None, size: Any = None, sort: Any = None) -> tuple:
        """Filters records based on search(q) and sorts them based on page, size, sort(sorting parameter)."""
        query = db.session.query(cls).filter(cls.account_uuid == account_uuid)

        if sort == SortingOrder.ASC.value:
            query = query.order_by(asc(cls.created_at))
        else:
            query = query.order_by(desc(cls.created_at))

        if q:
            query = query.filter(
                cls.email_type.ilike('%{}%'.format(q))  # type: ignore  # noqa: FKA100)
            )

        query_count = query.count()

        if page and size:
            offset = (int(page) - 1) * int(size)
            query = query.limit(int(size))
            query = query.offset(offset)

        return query.all(), query_count

    @classmethod
    def serialize(cls, details: Any) -> list:
        """ Make a list of Email Template objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            single_data_obj = {
                'id': single_data.id,
                'uuid': single_data.uuid,
                'account_uuid': single_data.account_uuid,
                'email_name': EmailTypes.get_email_template_name_by_email_type(single_data.email_type),
                'email_type': single_data.email_type,
                'email_subject': single_data.email_subject,
                'email_body': single_data.email_body,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }
            data.append(single_data_obj)
        return data
