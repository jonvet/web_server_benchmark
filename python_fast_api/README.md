# Python FastAPI server

Simple FastAPI web server.


## Usage

1. Set up your database:
```
uv run alembic upgrade head
```

2. Run the server:
```
uv run uvicorn src.main:app
```

use the `--reload` flag to automatically reload the server when you make changes to the code.

use the `--workers x` flag to run the server with x workers.
