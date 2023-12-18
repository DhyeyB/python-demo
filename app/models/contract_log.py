from datetime import datetime
from typing import Any
from sqlalchemy.orm import backref
from app import db
from app.models.account import Account
from app.models.base import Base
from app.models.contract import Contract
from sqlalchemy import ForeignKey


class ContractLog(Base):
    __tablename__ = 'contract_log'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    contract_uuid = db.Column(
        db.String, ForeignKey(Contract.uuid), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship('Account', backref=backref('contract_log', passive_deletes=True))

    @classmethod
    def get_by_account_and_contract(cls, account_uuid: str, contract_uuid: str):
        """Get all logs of that given contract"""
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(cls.contract_uuid == contract_uuid).all()

    @classmethod
    def serialize(cls, details: Any) -> list:
        """ Make a list of Contract Log objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            single_data_obj = {
                'id': single_data.id,
                'uuid': single_data.uuid,
                'account_uuid': single_data.account_uuid,
                'contract_uuid': single_data.contract_uuid,
                'description': single_data.description,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }
            data.append(single_data_obj)
        return data
