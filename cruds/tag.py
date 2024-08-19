from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.models import Task, Tag
from schemas import CreateUpdateTag, TagSchema, TokenData
from database.db import get_db
from cruds.auth import Autharization

auth = Autharization()

tag_router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    dependencies=[Depends(auth.auth_wrapper)],
)


@tag_router.get("/", response_model=list[TagSchema])
async def get_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()


@tag_router.post("/", response_model=TagSchema, status_code=status.HTTP_201_CREATED)
async def create_tag(tag: CreateUpdateTag, db:Session=Depends(get_db)):
    tag = Tag(name=tag.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@tag_router.get("/tags/{tag_id}", response_model=TagSchema)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag


@tag_router.put("/tags/{tag_id}", response_model=TagSchema)
def update_tag(tag_id: int, tag: CreateUpdateTag, db: Session = Depends(get_db)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    db_tag.name = tag.name
    db.commit()
    db.refresh(db_tag)
    return db_tag


@tag_router.delete("/tags/{tag_id}", response_model=TagSchema)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(db_tag)
    db.commit()
    return db_tag
