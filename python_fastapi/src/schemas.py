from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    name: str
    done: bool


class NewTask(TaskBase):
    pass


class Task(TaskBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
