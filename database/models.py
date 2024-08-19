from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from database.db import Base

task_tag_association_table = Table(
    'task_tag', Base.metadata,
    Column("task_id", Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    email = Column(String, unique=True)
    tasks = relationship("Task", back_populates="owner", cascade="all, delete")


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="tasks")
    tags = relationship("Tag", secondary=task_tag_association_table, back_populates="tasks")


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    tasks = relationship("Task", secondary=task_tag_association_table, back_populates="tags")
