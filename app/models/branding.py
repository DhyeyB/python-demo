from datetime import datetime
from app import db
from app.models.base import Base
from app.models.account import Account
from sqlalchemy import ForeignKey
from typing import Any
from workers.s3_worker import get_presigned_url
from sqlalchemy.orm import backref


class Branding(Base):
    __tablename__ = 'branding'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    company_logo = db.Column(db.String, nullable=True)
    cover_page = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship('Account', backref=backref('branding', passive_deletes=True))

    @staticmethod
    def get_branding_details_by_account_uuid(account_uuid):
        """Return branding details by account uuid."""
        return db.session.query(Branding).filter(Branding.account_uuid == account_uuid).first()

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
                'company_logo': get_presigned_url(single_data.company_logo),
                'cover_page': single_data.cover_page,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at
            }

            data.append(single_data_obj)
        if single_object:
            # If single_object is True, return the first item as a single object
            return data[0] if data else None
        else:
            return data
