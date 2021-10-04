from typing import Optional
import yaml


class Config:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.data = self.yaml_load(filename=filename)

    @staticmethod
    def yaml_load(filename: str) -> dict:
        with open(filename, encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
        return data

    def mode(self, name: str) -> Optional[dict]:
        return self.data.get(name, None)
