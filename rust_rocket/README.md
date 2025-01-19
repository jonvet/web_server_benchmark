# Rust Rocket server

Simple Rocket web server.


## Usage

1. Set up your database:

Create a `.env` file with the following content:
```
echo "DATABASE_URL=file:db.sqlite" > .env
```

Make sure you have diesel installed. If not, install it with:
```
cargo install diesel_cli --no-default-features --features sqlite
```

Then setup the sqlite database:
```
diesel setup
```

2. Run the server:
```
cargo run
```

or compile the server for release with:
```
cargo run --release
```
