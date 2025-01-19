mod crud;
mod models;
mod schema;

#[macro_use]
extern crate rocket;
use crate::crud::{create_task, delete_task, get_task, get_tasks, update_task};
use crate::models::{NewTask, Task};
use rocket::http::Status;
use rocket::serde::json::Json;
use rocket_sync_db_pools::{database, diesel};


#[database("sqlite_database")]
struct DbConn(diesel::SqliteConnection);

#[get("/")]
fn hello() -> &'static str {
    "Hello, world!"
}

#[get("/info")]
fn info() -> &'static str {
    "rocket"
}

#[post("/tasks", format = "json", data = "<task>")]
async fn create(task: Json<NewTask>, conn: DbConn) -> Json<Task> {
    conn.run(move |c| create_task(c, &task))
        .await
        .map(Json)
        .expect("Failed to create task")
}

#[get("/tasks")]
async fn index(conn: DbConn) -> Json<Vec<Task>> {
    conn.run(get_tasks)
        .await
        .map(Json)
        .expect("Failed to retrieve tasks")
}

#[get("/tasks/<id>")]
async fn detail(id: i32, conn: DbConn) -> Json<Task> {
    conn.run(move |c| get_task(c, id))
        .await
        .map(Json)
        .expect("Failed to retrieve task")
}

#[put("/tasks/<id>", format = "json", data = "<task>")]
async fn update(id: i32, task: Json<NewTask>, conn: DbConn) -> Json<Task> {
    conn.run(move |c| update_task(c, id, &task))
        .await
        .map(Json)
        .expect("Failed to update task")
}

#[delete("/tasks/<id>")]
async fn delete(id: i32, conn: DbConn) -> Status {
    conn.run(move |c| delete_task(c, id))
        .await
        .map(|num_deleted| {
            if num_deleted > 0 {
                Status::NoContent
            } else {
                Status::NotFound
            }
        })
        .unwrap_or(Status::InternalServerError)
}

#[rocket::main]
async fn main() -> Result<(), rocket::Error> {
    rocket::build()
        .attach(DbConn::fairing())
        .mount(
            "/",
            routes![hello, info, index, create, detail, update, delete],
        )
        .launch()
        .await?;

    Ok(())
}
