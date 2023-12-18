from datetime import datetime
from typing import Any, Union
from sqlalchemy import func, case
from app import db
from app.helpers.constants import SortingOrder, ContractStatus, ContractMailStatus, DurationType, PaymentFrequency
from app.models.account import Account
from app.models.base import Base
from app.models.client import Client
from app.models.template import Template
from app.models.user import User
from sqlalchemy import ForeignKey, asc, desc, or_
from app import app
from sqlalchemy.orm import relationship
from app.models.folder import Folder
from sqlalchemy.orm import backref


class Contract(Base):
    __tablename__ = 'contract'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    created_by = db.Column(db.String, ForeignKey(User.uuid), nullable=False)
    purpose = db.Column(db.String, nullable=False)
    client_uuid = db.Column(db.String, ForeignKey(Client.uuid), nullable=False)
    template_uuid = db.Column(
        db.String, ForeignKey(Template.uuid), nullable=True)
    folder_uuid = db.Column(db.String, ForeignKey(Folder.uuid), nullable=False)
    content = db.Column(db.Text, nullable=False)
    signed_content = db.Column(db.Text, nullable=False)
    brief = db.Column(db.Text, nullable=False)
    service_name = db.Column(db.String, nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    duration_type = db.Column(
        db.String, nullable=True, server_default=DurationType.MONTH.value)
    amount = db.Column(db.Float, nullable=True)
    payment_frequency = db.Column(
        db.String, nullable=True, server_default=PaymentFrequency.ONE_TIME.value)
    vat_percentage = db.Column(db.Float, nullable=True)
    currency_code = db.Column(db.String(3), nullable=True)
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    created_by_uuid = relationship(User, foreign_keys=[created_by])
    created_for_client_uuid = relationship(Client, foreign_keys=[client_uuid])

    account = db.relationship('Account', backref=backref(
        'contract', passive_deletes=True))

    @classmethod
    def serialize(cls, details: Any) -> list:
        """ Make a list of dictionary from objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            created_by_uuid = User.serialize(
                single_data.created_by_uuid, single_object=True)
            created_for_client_uuid = Client.serialize(
                single_data.created_for_client_uuid, single_object=True)

            from app.models.contract_signee import ContractSignee
            signed_count = ContractSignee.get_count_by_contact_uuid_and_status(contract_uuid=single_data.uuid,
                                                                               status=ContractMailStatus.SIGNED.value)
            is_editable = False
            if signed_count == 0 and single_data.status in [ContractStatus.DRAFT.value,
                                                            ContractStatus.SENT_FOR_SIGNING.value]:
                is_editable = True

            single_data_obj = {
                'id': single_data.id,
                'uuid': single_data.uuid,
                'account_uuid': single_data.account_uuid,
                'created_by': created_by_uuid,
                'purpose': single_data.purpose,
                'client_uuid': created_for_client_uuid,
                'template_uuid': single_data.template_uuid,
                'folder_uuid': single_data.folder_uuid,
                'content': single_data.content,
                'signed_content': single_data.signed_content,
                'brief': single_data.brief,
                'service_name': single_data.service_name,
                'duration': single_data.duration,
                'duration_type': single_data.duration_type,
                'currency_code': single_data.currency_code,
                'amount': single_data.amount,
                'payment_frequency': single_data.payment_frequency,
                'vat_percentage': single_data.vat_percentage,
                'status': single_data.status,
                'is_editable': is_editable,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }

            data.append(single_data_obj)
        return data

    @classmethod
    def get_contracts_list(cls, account_uuid: str, folder_uuid: Union[str, None] = None, q: Any = None, sort: Any = None, page: Any = None,
                           size: Any = None) -> tuple:
        """Filters records based on search(q) and sorts them based on page, size, sort(sorting parameter)."""

        query = db.session.query(cls).join(Client, cls.client_uuid == Client.uuid).filter(
            cls.account_uuid == account_uuid)

        if folder_uuid is not None:
            query = query.filter(cls.folder_uuid == folder_uuid)

        if sort == SortingOrder.ASC.value:
            query = query.order_by(asc(cls.created_at))
        else:
            query = query.order_by(desc(cls.created_at))

        if q:
            query = query.filter(
                or_(cls.purpose.ilike('%{}%'.format(q)),  # type: ignore  # noqa: FKA100
                    cls.brief.ilike('%{}%'.format(q)),
                    Client.legal_name.ilike('%{}%'.format(q)))
            )

        query_count = query.count()

        if page and size:
            offset = (int(page) - 1) * int(size)
            query = query.limit(int(size))
            query = query.offset(offset)

        return query.all(), query_count

    @classmethod
    def get_contracts_status_details(cls, account_uuid: Union[str, None] = None, start_timestamp: Union[int, None] = None,
                                     end_timestamp: Union[int, None] = None):
        """Return contracts by account uuid."""

        query = db.session.query(
            func.count(cls.uuid).label('count'),
            func.sum(case((cls.vat_percentage.is_(None), cls.amount),
                          else_=cls.amount * (1 + (cls.vat_percentage / 100)))).label('amount'),
            cls.status
        )

        if account_uuid:
            query = query.filter(cls.account_uuid == account_uuid)

        if start_timestamp is not None:
            start_date = datetime.utcfromtimestamp(start_timestamp)
            query = query.filter(cls.created_at >= start_date)

        if end_timestamp is not None:
            end_date = datetime.utcfromtimestamp(end_timestamp)
            query = query.filter(cls.created_at <= end_date)

        contracts = query.group_by(cls.status).all()

        return contracts

    @staticmethod
    def get_all_client_with_contract_count(q: Any = None, sort: Any = None, page: Any = None, size: Any = None) -> tuple:
        """
        Get all records of clients. Then
        Filter records based on search(q) and sorts them based on page, size, sort(sorting parameter).
        """
        query = db.session.query(                               # type: ignore  # noqa: FKA100
            Client.uuid,
            Client.legal_name,
            Account.legal_name.label('account_legal_name'),
            Client.display_name,
            Client.email,
            Client.created_at,
            func.count(Contract.uuid).label('contract_count')
        ).outerjoin(
            Contract, Client.uuid == Contract.client_uuid
        ).join(
            Account, Client.account_uuid == Account.uuid
        ).group_by(
            Account.legal_name,
            Client.uuid,
            Client.legal_name,
            Client.display_name,
            Client.email,
            Client.created_at
        )

        if sort == SortingOrder.ASC.value:
            query = query.order_by(asc(Client.created_at))
        else:
            query = query.order_by(desc(Client.created_at))

        if q:
            query = query.filter(
                or_(Client.legal_name.ilike('%{}%'.format(q)),  # type: ignore  # noqa: FKA100
                    Client.display_name.ilike('%{}%'.format(q)),
                    Client.email.ilike('%{}%'.format(q))
                    )
            )

        query_count = query.count()

        if page and size:
            offset = (int(page) - 1) * int(size)
            query = query.limit(int(size))
            query = query.offset(offset)

        return query.all(), query_count

    @classmethod
    def get_by_status(cls, account_uuid: str, status: str):
        """Get all contracts of all accounts with "sent for signing" status"""
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(cls.status == status).all()

    @classmethod
    def get_uuid_by_status(cls, status):
        """Get all contracts of all accounts with "sent for signing" status"""
        with app.app_context():
            return db.session.query(cls.uuid).filter(cls.status == status).all()

    @classmethod
    def get_folder_contact_count(cls, account_uuid: str, folder_uuid: str):
        """Get Contract count by account's folder_uuid"""
        return db.session.query(cls.uuid).filter(cls.account_uuid == account_uuid).filter(cls.folder_uuid == folder_uuid).count()
