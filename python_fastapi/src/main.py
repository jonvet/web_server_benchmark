import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from src.schemas import Task, NewTask
from src.db import get_db
import src.crud as crud

app = FastAPI()


@app.get("/")
async def hello() -> str:
    return "Hello, world!"


@app.get("/info")
async def info() -> str:
    return "fastapi"  # to identify the server in benchmark script


@app.post("/tasks", response_model=Task)
def create_task(task: NewTask, db: Session = Depends(get_db)):
    return crud.create_task(db, task)


@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: str, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.get("/tasks/", response_model=List[Task])
def read_tasks(db: Session = Depends(get_db)):
    return crud.get_tasks(db)


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, task: NewTask, db: Session = Depends(get_db)):
    db_task = crud.update_task(db, task_id, task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.delete("/tasks/{task_id}", response_model=int)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    deleted_count = crud.delete_task(db, task_id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return deleted_count


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
