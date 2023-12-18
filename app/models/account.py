from datetime import datetime
from typing import Any
from app import db
from app.helpers.constants import SortingOrder, UserType
from app.models.base import Base
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import or_, and_
from app import app
from bombaysoftwares_pysupp import str_to_bool


class Account(Base):
    __tablename__ = 'account'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    reference_customer_id = db.Column(
        db.String(255), nullable=True, unique=True)
    legal_name = db.Column(db.String, nullable=True)
    display_name = db.Column(db.String, nullable=True)
    postal_code = db.Column(db.String, nullable=True)
    address = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=True)
    state = db.Column(db.String, nullable=True)
    country = db.Column(db.String, nullable=True)
    currency_code = db.Column(db.String(3), nullable=True)
    vat_percentage = db.Column(db.String, nullable=True)
    deletion_scheduled_at = db.Column(db.Integer, nullable=True)
    deactivated_at = db.Column(db.DateTime, server_default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    @classmethod
    def get_all_with_not_null_legal_name_display_name(cls) -> list:
        """Get account with subscription"""
        return db.session.query(cls).filter(cls.legal_name != '').filter(cls.display_name != '').all()

    @staticmethod
    def get_account_by_reference_customer_id(reference_customer_id) -> list:
        """Return account by reference customer id."""
        return db.session.query(Account).filter(Account.reference_customer_id == reference_customer_id).first()

    @classmethod
    def get_delete_scheduled_accounts(cls):
        """
            Class method to fetch/select the accounts which are scheduled to delete at current time.
        """
        with app.app_context():
            today_timestamp = int(datetime.combine(datetime.now().date(), datetime.min.time()).timestamp())  # type: ignore  # noqa: FKA100
            return db.session.query(cls).filter(
                and_(cls.deletion_scheduled_at.is_not(None), cls.deletion_scheduled_at == today_timestamp),  # type: ignore  # noqa: FKA100
            ).all()

    @classmethod
    def get_account_list(cls, q: Any = None, sort: Any = None, page: Any = None, size: Any = None, download: str = 'False') -> tuple:
        """Filters records based on search(q) and sorts them based on page, size, sort(sorting parameter)."""
        from app.models.user import User
        if download and str_to_bool(download):
            return db.session.query(cls.legal_name, cls.display_name, cls.postal_code, cls.address, cls.city, cls.state,
                                    cls.country, User.first_name, User.last_name).join(User, cls.uuid == User.account_uuid).filter(
                User.user_type == UserType.PRIMARY_USER.value).all()

        query = db.session.query(cls.id, cls.uuid, cls.legal_name, cls.display_name, cls.postal_code, cls.address, cls.city, cls.state,
                                 cls.country, User.first_name, User.last_name, User.uuid.label('user_uuid')).join(User, cls.uuid == User.account_uuid).filter(
            User.user_type == UserType.PRIMARY_USER.value)

        if sort == SortingOrder.ASC.value:
            query = query.order_by(asc(cls.created_at))
        else:
            query = query.order_by(desc(cls.created_at))

        if q:
            query = query.filter(
                or_(cls.legal_name.ilike('%{}%'.format(q)),  # type: ignore  # noqa: FKA100
                    cls.display_name.ilike('%{}%'.format(q)),
                    cls.postal_code.ilike('%{}%'.format(q)),
                    cls.address.ilike('%{}%'.format(q)),
                    cls.city.ilike('%{}%'.format(q)),
                    cls.state.ilike('%{}%'.format(q)),
                    cls.country.ilike('%{}%'.format(q)),
                    User.first_name.ilike('%{}%'.format(q)),
                    User.last_name.ilike('%{}%'.format(q))
                    )
            )

        query_count = query.count()

        if page and size:
            offset = (int(page) - 1) * int(size)
            query = query.limit(int(size))
            query = query.offset(offset)

        return query.all(), query_count

    @classmethod
    def serialize(cls, details: Any) -> list:
        """ Make a list of Accounts objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            single_data_obj = {
                'id': single_data.id,
                'uuid': single_data.uuid,
                'reference_customer_id': single_data.reference_customer_id,
                'legal_name': single_data.legal_name,
                'display_name': single_data.display_name,
                'postal_code': single_data.postal_code,
                'address': single_data.address,
                'city': single_data.city,
                'state': single_data.state,
                'country': single_data.country,
                'currency_code': single_data.currency_code,
                'vat_percentage': single_data.vat_percentage,
                'deletion_scheduled_at': single_data.deletion_scheduled_at,
                'deactivated_at': single_data.deactivated_at,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }
            data.append(single_data_obj)
        return data
