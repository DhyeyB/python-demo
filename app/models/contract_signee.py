from datetime import datetime
from typing import Any
from sqlalchemy.orm import backref
from app import db
from app.helpers.constants import ContractMailStatus
from app.models.account import Account
from app.models.base import Base
from app.models.client import Client
from app.models.contract import Contract
from app.models.signee import Signee
from sqlalchemy import ForeignKey, asc
from app import app


class ContractSignee(Base):
    __tablename__ = 'contract_signee'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    contract_uuid = db.Column(
        db.String, ForeignKey(Contract.uuid), nullable=False)
    client_uuid = db.Column(
        db.String, ForeignKey(Client.uuid), nullable=False)
    signee_uuid = db.Column(db.String, ForeignKey(Signee.uuid), nullable=False)
    signee_email = db.Column(db.String, nullable=False)
    signee_full_name = db.Column(db.String, nullable=False)
    signee_signature = db.Column(db.Text, nullable=True)
    signature_type = db.Column(db.String, nullable=True)
    signee_ip = db.Column(db.String, nullable=True)
    signed_at = db.Column(db.BigInteger, nullable=True)
    status = db.Column(db.String, nullable=False)
    is_account_signee = db.Column(
        db.Boolean, default=False, server_default='f', nullable=False)
    signee_priority = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship('Account', backref=backref(
        'contract_signee', passive_deletes=True))

    @classmethod
    def get_by_account_and_contract(cls, account_uuid: str, contract_uuid: str) -> list:
        """Get objects by given contract_uuid"""
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(cls.contract_uuid == contract_uuid).all()

    @classmethod
    def get_by_account_client_and_contract(cls, account_uuid: str, client_uuid: str, contract_uuid: str) -> list:
        """Get all signee uuids by account uuid, client uuid and contract uuid. """
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(
            cls.client_uuid == client_uuid).filter(cls.contract_uuid == contract_uuid).all()

    @classmethod
    def get_highest_priority_signee(cls, account_uuid: str, contract_uuid: str) -> Any:
        """Get the highest priority signee of given contract"""
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(cls.contract_uuid == contract_uuid).filter(cls.status != ContractMailStatus.SIGNED.value).order_by(asc(cls.signee_priority)).first()

    @classmethod
    def get_next_signee(cls, contract_uuid: str, signee_priority: int) -> Any:
        """Get the next signee of given signee"""
        return db.session.query(cls).filter(cls.contract_uuid == contract_uuid).filter(
            cls.signee_priority > signee_priority).order_by(asc(cls.signee_priority)).first()

    @classmethod
    def get_by_account_contact_and_status(cls, account_uuid: str, contract_uuid: str, status_list: list) -> list:
        """Get count of signee by given status and contract"""
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(cls.contract_uuid == contract_uuid).filter(cls.status.in_(status_list)).all()

    @classmethod
    def get_count_by_contact_uuid_and_status(cls, status: str, contract_uuid: str) -> int:
        """Get count of signee by given status and contract"""
        return db.session.query(cls).filter(cls.contract_uuid == contract_uuid).filter(cls.status == status).count()

    @classmethod
    def get_email_by_contact_uuids_and_status(cls, status: str, contract_uuids: list) -> list:
        """Get email ids of given contract by its status"""
        with app.app_context():
            return db.session.query(cls.uuid, cls.signee_email, cls.signee_full_name, cls.account_uuid, cls.contract_uuid).filter(cls.contract_uuid.in_(contract_uuids)).filter(cls.status == status).all()

    @classmethod
    def delete_by_contract(cls, account_uuid: str, contract_uuid: str, client_uuid: str) -> None:
        """Delete records by contract_uuid ."""
        db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(cls.client_uuid == client_uuid).filter(
            cls.contract_uuid == contract_uuid).delete()

    @classmethod
    def get_contract_signee_by_signee_uuid(cls, account_uuid: str, signee_uuid: str):
        """Get contract signee by signee uuid."""
        return db.session.query(cls.signee_uuid, cls.signee_email).filter(cls.account_uuid == account_uuid).filter(cls.signee_uuid == signee_uuid).first()

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
                'contract_uuid': single_data.contract_uuid,
                'client_uuid': single_data.client_uuid,
                'signee_uuid': single_data.signee_uuid,
                'signee_email': single_data.signee_email,
                'signee_full_name': single_data.signee_full_name,
                'signee_signature': single_data.signee_signature,
                'signee_ip': single_data.signee_ip,
                'signed_at': datetime.fromtimestamp(single_data.signed_at).strftime('%Y-%m-%d %H:%M:%S%p') if single_data.signed_at is not None else None,
                'status': single_data.status,
                'is_account_signee': single_data.is_account_signee,
                'signee_priority': single_data.signee_priority,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }

            data.append(single_data_obj)
        return data
