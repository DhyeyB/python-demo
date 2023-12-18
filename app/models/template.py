from datetime import datetime
from typing import Any
from sqlalchemy.orm import backref
from app import db
from app.models.account import Account
from app.models.base import Base
from app.models.user import User
from sqlalchemy import ForeignKey


class Template(Base):
    __tablename__ = 'template'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    created_by = db.Column(db.String, ForeignKey(User.uuid), nullable=False)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship('Account', backref=backref('template', passive_deletes=True))

    @staticmethod
    def get_template_by_account(account_id: int) -> list:
        """Return all templates associated with the specified account."""
        return db.session.query(Template).filter_by(account_id=account_id).all()

    @classmethod
    def serialize_template(cls, details: Any) -> list:
        """ Make a list of Template objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            single_data_obj = {
                'id': single_data.id,
                'user_id': single_data.user_id,
                'account_id': single_data.account_id,
                'name': single_data.name,
                'content': single_data.content,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }

            data.append(single_data_obj)

        return data
