use axum::{
    extract::{Path, State},
    http::StatusCode,
    routing::{get},
    Json, Router,
};
use diesel::{
    r2d2::{self, ConnectionManager},
    sqlite::SqliteConnection,
    connection::SimpleConnection,
};
use std::sync::Arc;
use std::time::Duration;

mod models;
mod crud;
mod schema;

use crate::models::{Task, NewTask};
use crate::crud::{create_task, delete_task, get_task, get_tasks, update_task};

type DbPool = Arc<r2d2::Pool<ConnectionManager<SqliteConnection>>>;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let runtime = tokio::runtime::Builder::new_multi_thread()
        .worker_threads(2) 
        .enable_all()
        .build()?;
    runtime.block_on(async_main())
}

async fn async_main() -> Result<(), Box<dyn std::error::Error>> {
    let database_url = "db.sqlite";
    let pool_size = 2;
    let manager = ConnectionManager::<SqliteConnection>::new(database_url);
    let pool = r2d2::Pool::builder()
        .max_size(pool_size)
        .connection_customizer(Box::new(ConnectionOptions {
            busy_timeout: Some(Duration::from_secs(5)),
            pragmas: vec![
                ("journal_mode".to_string(), "WAL".to_string()),
            ],
        }))
        .build(manager)
        .expect("Failed to create pool.");

    let pool = Arc::new(pool);

    let app = Router::new()
        .route("/", get(hello))
        .route("/info", get(info))
        .route("/tasks", get(index).post(create_task_handler))
        .route("/tasks/:id", get(detail).put(update_task_handler).delete(delete_task_handler))
        .with_state(pool);

    println!("Server starting on http://127.0.0.1:8000");
    axum::Server::bind(&"127.0.0.1:8000".parse().unwrap())
        .serve(app.into_make_service())
        .await?;

    Ok(())
}

#[derive(Debug)]
struct ConnectionOptions {
    pub busy_timeout: Option<Duration>,
    pub pragmas: Vec<(String, String)>,
}

impl r2d2::CustomizeConnection<SqliteConnection, diesel::r2d2::Error> for ConnectionOptions {
    fn on_acquire(&self, conn: &mut SqliteConnection) -> Result<(), diesel::r2d2::Error> {
        if let Some(duration) = self.busy_timeout {
            conn.batch_execute(&format!("PRAGMA busy_timeout = {};", duration.as_millis()))
                .map_err(diesel::r2d2::Error::QueryError)?;
        }

        for (name, value) in &self.pragmas {
            conn.batch_execute(&format!("PRAGMA {} = {};", name, value))
                .map_err(diesel::r2d2::Error::QueryError)?;
        }

        Ok(())
    }
}

async fn hello() -> &'static str {
    "Hello, world!"
}

async fn info() -> &'static str {
    "axum"
}

async fn create_task_handler(
    State(pool): State<DbPool>,
    Json(new_task): Json<NewTask>,
) -> Result<Json<Task>, (StatusCode, String)> {
    let mut conn = pool.get().map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
    create_task(&mut conn, &new_task)
        .map(Json)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to create task: {}", e)))
}

async fn index(State(pool): State<DbPool>) -> Result<Json<Vec<Task>>, (StatusCode, String)> {
    let mut conn = pool.get().map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
    get_tasks(&mut conn)
        .map(Json)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to get tasks: {}", e)))
}

async fn detail(
    State(pool): State<DbPool>,
    Path(id): Path<i32>,
) -> Result<Json<Task>, (StatusCode, String)> {
    let mut conn = pool.get().map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
    get_task(&mut conn, id)
        .map(Json)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to get task: {}", e)))
}

async fn update_task_handler(
    State(pool): State<DbPool>,
    Path(id): Path<i32>,
    Json(task): Json<NewTask>,
) -> Result<Json<Task>, (StatusCode, String)> {
    let mut conn = pool.get().map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
    update_task(&mut conn, id, &task)
        .map(Json)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to update task: {}", e)))
}

async fn delete_task_handler(
    State(pool): State<DbPool>,
    Path(id): Path<i32>,
) -> Result<StatusCode, (StatusCode, String)> {
    let mut conn = pool.get().map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
    delete_task(&mut conn, id)
        .map(|num_deleted| if num_deleted > 0 { StatusCode::NO_CONTENT } else { StatusCode::NOT_FOUND })
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to delete task: {}", e)))
}