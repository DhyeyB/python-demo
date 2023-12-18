from datetime import datetime
from typing import Any, Union
from sqlalchemy.orm import backref
from app import db
from app.models.account import Account
from app.models.base import Base
from app.models.client import Client
from app.models.user import User
from sqlalchemy import ForeignKey, asc


class Signee(Base):
    __tablename__ = 'signee'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    client_uuid = db.Column(db.String, ForeignKey(Client.uuid), nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    created_by = db.Column(db.String, ForeignKey(User.uuid), nullable=False)
    full_name = db.Column(db.String, nullable=False)
    job_title = db.Column(db.String)
    email = db.Column(db.String, nullable=False)
    signing_sequence = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship(
        'Account', backref=backref('signee', passive_deletes=True))

    @classmethod
    def get_by_email(cls, email: str) -> Any:
        return db.session.query(cls).filter(cls.email == email).first()

    @classmethod
    def get_all_by_client_uuid(cls, client_uuid: str, account_uuid: Union[str, None] = None) -> list:
        if account_uuid is None:
            return db.session.query(cls).filter(cls.client_uuid == client_uuid).order_by(asc(cls.signing_sequence)).all()
        else:
            return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(cls.client_uuid == client_uuid).order_by(asc(cls.signing_sequence)).all()

    @classmethod
    def get_all_signee_uuid_by_client_uuid(cls, account_uuid: str, client_uuid: str) -> list:
        return db.session.query(cls.uuid).filter(cls.account_uuid == account_uuid).filter(cls.client_uuid == client_uuid).all()

    @classmethod
    def check_if_email_already_exists(cls, account_uuid: str, email: str, signee_uuid: str = '') -> bool:
        """
        Check if signee with given email already exists.

        If signee_uuid: [Used in case of update signee API]
            check if signees with given email already exists except given signee.
        """

        if signee_uuid:
            return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(cls.uuid != signee_uuid).filter(cls.email == email).first() is not None
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(cls.email == email).first() is not None

    @classmethod
    def serialize(cls, details: Any) -> list:
        """Create a list of dictionaries from objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            single_data_obj = {
                'id': single_data.id,
                'uuid': single_data.uuid,
                'client_uuid': single_data.client_uuid,
                'account_uuid': single_data.account_uuid,
                'created_by': single_data.created_by,
                'full_name': single_data.full_name,
                'job_title': single_data.job_title,
                'email': single_data.email,
                'signing_sequence': single_data.signing_sequence,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }
            data.append(single_data_obj)

        return data
