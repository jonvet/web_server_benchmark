// @generated automatically by Diesel CLI.

diesel::table! {
    tasks (id) {
        id -> Integer,
        name -> Text,
        done -> Bool,
    }
}
