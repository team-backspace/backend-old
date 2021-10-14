from tortoise import Tortoise
from tortoise import run_async

class Database:
    def __init__(self, models) -> None:
        run_async(self.connect(models))

    @staticmethod
    async def connect(models):
        await Tortoise.init(
            db_url="sqlite://database/database.db",
            modules={"models" : models}
        )


if __name__ == "__main__":
    pass
