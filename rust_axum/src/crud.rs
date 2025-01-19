use crate::models::{NewTask, Task};
use crate::schema::tasks;
use diesel::prelude::*;
use diesel::sqlite::SqliteConnection;

pub fn create_task(conn: &mut SqliteConnection, new_task: &NewTask) -> QueryResult<Task> {
    conn.transaction(|conn| {
        diesel::insert_into(tasks::table)
            .values(new_task)
            .execute(conn)?;

        tasks::table.order(tasks::id.desc()).first(conn)
    })
}

pub fn get_task(conn: &mut SqliteConnection, task_id: i32) -> QueryResult<Task> {
    tasks::table.find(task_id).first(conn)
}

pub fn get_tasks(conn: &mut SqliteConnection) -> QueryResult<Vec<Task>> {
    tasks::table.load::<Task>(conn)
}

pub fn delete_task(conn: &mut SqliteConnection, task_id: i32) -> QueryResult<usize> {
    diesel::delete(tasks::table.find(task_id)).execute(conn)
}

pub fn update_task(
    conn: &mut SqliteConnection,
    task_id: i32,
    updated_task: &NewTask,
) -> QueryResult<Task> {
    diesel::update(tasks::table.find(task_id))
        .set(updated_task)
        .execute(conn)?;

    tasks::table.find(task_id).first(conn)
}