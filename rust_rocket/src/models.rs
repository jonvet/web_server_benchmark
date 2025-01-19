use diesel::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Queryable, Selectable, Serialize, Deserialize)]
#[diesel(table_name = crate::schema::tasks)]
#[diesel(check_for_backend(diesel::sqlite::Sqlite))]
pub struct Task {
    pub id: i32,
    pub name: String,
    pub done: bool,
}

#[derive(Insertable, AsChangeset, Deserialize)]
#[diesel(table_name = crate::schema::tasks)]
pub struct NewTask {
    pub name: String,
    pub done: bool,
}
