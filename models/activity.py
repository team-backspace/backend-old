from __future__ import annotations
from dataclasses import dataclass
from tortoise import fields


class ActivityField(fields.JSONField):
    def to_db_value(self, value: Activity, _) -> dict:
        return value.to_dict()

    def to_python_value(self, value: dict) -> Activity:
        return Activity(
            name=value["name"],
            description=value["description"],
            icon_url=value["icon_url"],
        )


@dataclass
class Activity:
    name: str
    description: str
    icon_url: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "icon_url": self.icon_url,
        }
