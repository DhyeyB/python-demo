from datetime import datetime
from typing import Any

from app import db
from app.models.base import Base


class Plan(Base):
    __tablename__ = 'plan'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    reference_plan_id = db.Column(db.String(255), nullable=True, unique=True)
    name = db.Column(db.String, nullable=False)
    period = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String, nullable=False)
    amount = db.Column(db.Numeric)
    discount = db.Column(db.Numeric, nullable=False)
    feature = db.Column(db.JSON, nullable=False)
    description = db.Column(db.Text)
    deactivated_at = db.Column(db.DateTime, server_default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    @staticmethod
    def get_plan_by_reference_plan_id(reference_plan_id) -> list:
        """Return plan by reference id."""
        return db.session.query(Plan).filter(Plan.reference_plan_id == reference_plan_id).first()

    @classmethod
    def serialize_plan(cls, details: Any, single_object: bool = False) -> Any:
        """ Make a list of Client objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            single_data_obj = {
                'id': single_data.id,
                'uuid': single_data.uuid,
                'reference_plan_id': single_data.reference_plan_id,
                'name': single_data.name,
                'status': single_data.status,
                'period': single_data.period,
                'amount': single_data.amount,
                'discount': single_data.discount,
                'feature': single_data.feature,
                'description': single_data.description,
                'deactivated_at': single_data.deactivated_at,
                'created_at': single_data.created_at,
                'updated_at': single_data.updated_at,
            }

            data.append(single_data_obj)
        if single_object:
            # If single_object is True, return the first item as a single object
            return data[0] if data else None
        else:
            return data
