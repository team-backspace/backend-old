from typing import List

from dataclasses import dataclass


@dataclass
class Error:
    error_code: str
    message: str

    def to_dict(self) -> dict:
        return {"code": self.error_code, "message": self.message}


@dataclass
class ErrorForm:
    error_code: int
    errors: List[Error]

    def to_dict(self) -> dict:
        return {
            "code": self.error_code,
            "errors": [error.to_dict() for error in self.errors],
        }
