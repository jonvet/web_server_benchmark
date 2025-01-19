from src.db import Base
from sqlalchemy import Column, String, Boolean, Integer


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    done = Column(Boolean, nullable=True)
