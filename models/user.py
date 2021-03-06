from __future__ import annotations
from dataclasses import dataclass
from tortoise import fields
from tortoise.models import Model

from models.activity import ActivityField, Activity


class User(Model):
    id = fields.TextField(pk=True)
    name = fields.TextField(default="새 유저")
    bio = fields.TextField(null=True, default="새로운 유저를 환영해주세요!")
    activity = ActivityField(
        null=True,
        default=Activity(
            name="작품 탐색중", description="Spacebook에서 작품을 살펴보는 중", icon_url=""
        ),
    )
    profile_url = fields.TextField(null=True, default="")
    banner_url = fields.TextField(null=True, default="")
    followers = fields.ManyToManyField(
        model_name="models.User", related_name="user_followers"
    )
    following = fields.ManyToManyField(
        model_name="models.User", related_name="user_following"
    )
    data = fields.JSONField(default={})


class LoginUser(Model):
    email = fields.TextField(pk=True)
    id = fields.TextField(default=None)
    password = fields.TextField(default=None)
    trusted_device = fields.JSONField(default={"devices": []})


class VerifyEmail(Model):
    code = fields.TextField(pk=True)
    data = fields.JSONField(default={})


class AuthorizationStorage(Model):
    key = fields.TextField(pk=True)
    id = fields.TextField(default=None)
    name = fields.TextField(default="유저")
