from __future__ import annotations
from tortoise import fields
from tortoise.models import Model


class FundQueue(Model):
    id = fields.TextField(pk=True)
    user_id = fields.TextField(default=None)
    action_data = fields.JSONField(default={"name": "fund_project", "target_id": 1234})
    name = fields.TextField(default="새 결제 대기열")
    reason = fields.TextField(default="새 결제")
    amount = fields.JSONField(default={"currency": "USD", "amount": 0})
    payment_completed = fields.BooleanField(default=False)
