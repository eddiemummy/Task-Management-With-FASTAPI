from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from database.models import Task, Tag, User
from schemas import TaskSchema, CreateTask, UpdateTask, TokenData, TagSchema
from cruds.auth import Autharization
from database.db import get_db

task_router = APIRouter(
    prefix="/tasks",
    tags=['tasks'],
)

auth = Autharization()


@task_router.post('/', response_model=TaskSchema)
async def create_task(task: CreateTask, db: Session = Depends(get_db), user: TokenData = Depends(auth.auth_wrapper)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority
    )

    for tag_id in task.tag_ids:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if tag:
            new_task.tags.append(tag)

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@task_router.get("/tasks/{task_id}", response_model=TaskSchema)
def read_task(task_id: int, db: Session = Depends(get_db), user: TokenData = Depends(auth.auth_wrapper)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@task_router.put("/tasks/{task_id}", response_model=TaskSchema)
async def update_task(task: UpdateTask, task_id: int, db: Session = Depends(get_db),
                      user: TokenData = Depends(auth.auth_wrapper)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.title = task.title
    db_task.description = task.description
    db_task.priority = task.priority
    db_task.completed = task.completed
    if task.tag_ids:
        db_task.tags = []
        for tag_id in task.tag_ids:
            db_task.tags.append(db.query(Tag).filter(Tag.id == tag_id).first())
    db.commit()
    return db_task


@task_router.delete("/tasks/{task_id}", response_description="Task deleted")
async def delete_task(task_id: int, db: Session = Depends(get_db), user: TokenData = Depends(auth.auth_wrapper)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="Task deleted")


@task_router.post("/tasks/{task_id}/tags/{tag_id}", response_model=TaskSchema)
async def add_tag_to_task(task_id: int, tag_id: int, db: Session = Depends(get_db),
                          user: TokenData = Depends(auth.auth_wrapper)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if db_tag not in db_task.tags:
        db_task.tags.append(db_tag)
        db.commit()
    return db_task


@task_router.delete("/tasks/{task_id}/tags/{tag_id}", response_description="Tag deleted")
async def remove_tag_from_task(task_id: int, tag_id: int, db: Session = Depends(get_db),
                               user: TokenData = Depends(auth.auth_wrapper)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if db_tag not in db_task.tags:
        db_task.tags.remove(db_tag)
        db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="Tag deleted")


@task_router.get("/tasks/{task_id}/tags", response_model= list[TagSchema])
async def get_tags_of_task(task_id: int, db: Session = Depends(get_db),
                           user: TokenData = Depends(auth.auth_wrapper)):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    return task.tags

