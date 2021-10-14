from fastapi import FastAPI
from utils import Database
import models

Database(models)
# from router.user import login, profile

app = FastAPI()

# app.include_router(login.router)
# app.include_router(profile.router)

@app.get("/")
async def root():
    return { "hello" : "world" }

Database(models)