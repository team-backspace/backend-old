from __future__ import annotations
from typing import Optional, List
from ast import literal_eval
from dataclasses import dataclass
from tortoise import fields
from tortoise.models import Model


class ProjectAuthorField(fields.JSONField):
    def to_db_value(self, value: ProjectAuthor, _) -> dict:
        return value.to_dict()

    def to_python_value(self, value: dict) -> ProjectAuthor:
        return ProjectAuthor(
            id=value.get("id"),
            name=value["name"],
            profile_url=value.get("profile_url"),
            is_registered=value["is_registered"],
        )


@dataclass
class ProjectAuthor:
    id: Optional[str]
    name: str
    profile_url: Optional[str]
    is_registered: bool

    def to_dict(self) -> dict:
        return {
            "id": "" if not self.id else self.id,
            "name": self.name,
            "profile_url": "" if not self.profile_url else self.profile_url,
            "is_registered": self.is_registered,
        }


class ReactionsField(fields.TextField):
    def to_db_value(self, value: List[Reaction], _) -> str:
        return str([reaction.to_dict() for reaction in value])

    def to_python_value(self, value: str) -> List[Reaction]:
        dict_value = literal_eval(value)
        return [
            Reaction(
                id=data["id"],
                emoji=data["emoji"],
                count=data["count"],
                react_users=data["react_users"],
            )
            for data in dict_value
        ]


@dataclass
class Reaction:
    id: str
    emoji: str
    count: int
    react_users: List[int]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "emoji": self.emoji,
            "count": self.count,
            "react_users": self.react_users,
        }


class Project(Model):
    id = fields.TextField(pk=True)
    name = fields.TextField(default="새 작품")
    description = fields.TextField(null=True, default="방금 생성된 빈 작품")
    author = ProjectAuthorField(default=None)
    project_type = fields.TextField(default="blank")
    reactions = ReactionsField(default=[])
