from datetime import datetime
from typing import Any
from sqlalchemy import desc
from app import db
from app.models.account import Account
from app.models.base import Base
from app.models.plan import Plan
from sqlalchemy import ForeignKey
from app.helpers.constants import SubscriptionStatus
from sqlalchemy.orm import backref
from app import app
from app import logger
from sqlalchemy import or_


class Subscription(Base):
    __tablename__ = 'subscription'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    reference_subscription_id = db.Column(
        db.String(255), nullable=True, unique=True)
    account_uuid = db.Column(
        db.String, ForeignKey(Account.uuid, ondelete='CASCADE'), nullable=False)
    plan_uuid = db.Column(db.String, db.ForeignKey(Plan.uuid), nullable=False)
    status = db.Column(db.String, nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    trial_period_end_date = db.Column(db.DateTime, nullable=True)
    deactivated_at = db.Column(db.DateTime, server_default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship('Account', backref=backref(
        'subscription', passive_deletes=True))

    @staticmethod
    def get_active_subscription_by_account_uuid(account_uuid: str):
        """Return active subscription by account uuid."""
        return db.session.query(Subscription).filter(Subscription.account_uuid == account_uuid, Subscription.status == SubscriptionStatus.ACTIVE.value).first()

    @classmethod
    def get_latest_inactive_subscription_by_account_uuid(cls, account_uuid: str):
        """
            Return latest inactive subscription by account uuid.
            This function is used in stripe webhook call to get the latest subscription entry.
        """
        return db.session.query(Subscription).filter(Subscription.account_uuid == account_uuid, Subscription.status == SubscriptionStatus.INACTIVE.value).order_by(desc(cls.created_at)).first()

    @classmethod
    def update_all_expired_subscriptions(cls):
        """
            Update status of all expired subscriptions from active to expired.
        """
        with app.app_context():
            logger.info('Subscription status update Started.')
            today = datetime.now()
            db.session.query(cls).filter(cls.status == SubscriptionStatus.ACTIVE.value, cls.end_date < today).update(
                {cls.status: SubscriptionStatus.EXPIRED.value},
                synchronize_session=False  # Set to False for a bulk update
            )
            db.session.commit()
            logger.info('Subscription status update completed.')

    @classmethod
    def get_expired_or_cancelled_subscription(cls, account_uuid: str):
        """
            Return latest expired or cancelled subscription by account uuid
        """
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(or_(Subscription.status == SubscriptionStatus.EXPIRED.value, Subscription.status == SubscriptionStatus.CANCELLED.value)).order_by(desc(cls.created_at)).first()

    @classmethod
    def check_has_used_free_trial(cls, account_uuid: str):
        """
            check whether a user has already used a free trial by account uuid
        """
        return db.session.query(cls).filter(cls.account_uuid == account_uuid).filter(cls.status.in_([SubscriptionStatus.EXPIRED.value, SubscriptionStatus.CANCELLED.value, SubscriptionStatus.ACTIVE.value])).count() > 0

    @classmethod
    def serialize_subscription(cls, details: Any, single_object: bool = False) -> Any:
        """ Make a list of Client objects"""
        if not isinstance(details, list):
            details = [details]
        data = []
        for single_data in details:
            single_data_obj = {
                'id': single_data.id,
                'uuid': single_data.uuid,
                'reference_subscription_id': single_data.reference_subscription_id,
                'account_uuid': single_data.account_uuid,
                'plan_uuid': single_data.plan_uuid,
                'status': single_data.status,
                'start_date': single_data.start_date,
                'end_date': single_data.end_date,
                'trial_period_end_date': single_data.trial_period_end_date,
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
