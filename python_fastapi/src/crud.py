from sqlalchemy.orm import Session
from . import models, schemas


def create_task(db: Session, task: schemas.NewTask):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    return schemas.Task.model_validate(db_task)


def get_task(db: Session, task_id: str):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    return schemas.Task.model_validate(db_task) if db_task else None


def get_tasks(db: Session):
    db_tasks = db.query(models.Task).all()
    return [schemas.Task.model_validate(task) for task in db_tasks]


def update_task(db: Session, task_id: str, task: schemas.NewTask):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        for key, value in task.model_dump().items():
            setattr(db_task, key, value)
        db.commit()
        return schemas.Task.model_validate(db_task)
    return None


def delete_task(db: Session, task_id: str):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return 1
    return 0
