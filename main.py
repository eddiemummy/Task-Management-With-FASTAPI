from fastapi import FastAPI
from cruds.tag import tag_router
from cruds.task import task_router
from cruds.user import user_router
from database import models
from database.db import engine

app = FastAPI()
app.include_router(user_router)
app.include_router(tag_router)
app.include_router(task_router)

models.Base.metadata.create_all(bind=engine)

