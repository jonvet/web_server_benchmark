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

#[derive(Insertable, AsChangeset, Deserialize, Clone)]
#[diesel(table_name = crate::schema::tasks)]
pub struct NewTask {
    pub name: String,
    #[serde(deserialize_with = "deserialize_bool_from_string_or_bool")]
    pub done: bool,
}

fn deserialize_bool_from_string_or_bool<'de, D>(deserializer: D) -> Result<bool, D::Error>
where
    D: serde::Deserializer<'de>,
{
    #[derive(Deserialize)]
    #[serde(untagged)]
    enum BoolOrString {
        Bool(bool),
        String(String),
    }

    match BoolOrString::deserialize(deserializer)? {
        BoolOrString::Bool(b) => Ok(b),
        BoolOrString::String(s) => match s.to_lowercase().as_str() {
            "true" => Ok(true),
            "false" => Ok(false),
            "True" => Ok(true),
            "False" => Ok(false),
            _ => Err(serde::de::Error::custom("can't deserialize string to bool")),
        },
    }
}