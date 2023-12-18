from datetime import datetime
from typing import Any

from app import db
from app.helpers.constants import SortingOrder
from app.models.base import Base
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import or_


class ContactUs(Base):
    __tablename__ = 'contact_us'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String, nullable=False)
    company_size = db.Column(db.BigInteger, nullable=True)
    company_name = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

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
                'first_name': single_data.first_name,
                'last_name': single_data.last_name,
                'email': single_data.email,
                'company_size': single_data.company_size,
                'company_name': single_data.company_name,
                'message': single_data.message,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }

            data.append(single_data_obj)
        return data

    @classmethod
    def get_contact_us_list(cls, q: Any = None, sort: Any = None, page: Any = None, size: Any = None) -> tuple:
        """Filters records based on search(q) and sorts them based on page, size, sort(sorting parameter)."""
        query = db.session.query(cls)

        if sort == SortingOrder.ASC.value:
            query = query.order_by(asc(cls.created_at))
        else:
            query = query.order_by(desc(cls.created_at))

        if q:
            query = query.filter(
                or_(cls.first_name.ilike('%{}%'.format(q)),  # type: ignore  # noqa: FKA100
                    cls.last_name.ilike('%{}%'.format(q)),
                    cls.email.ilike('%{}%'.format(q)),
                    cls.company_name.ilike('%{}%'.format(q)),
                    cls.message.ilike('%{}%'.format(q)))
            )

        query_count = query.count()

        if page and size:
            offset = (int(page) - 1) * int(size)
            query = query.limit(int(size))
            query = query.offset(offset)

        return query.all(), query_count
