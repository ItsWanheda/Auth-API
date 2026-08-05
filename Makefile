.PHONY: help install run test lint format migrate upgrade down clean

help:
    @echo "Targets: install run test lint format migrate upgrade down clean"

install:
    pip install -r requirements.txt

run:
    uvicorn app.main:app --reload

test:
    pytest -v --cov=app

lint:
    ruff check .

format:
    ruff format .

migrate:
    alembic revision --autogenerate -m "$(name)"

upgrade:
    alembic upgrade head

down:
    alembic downgrade -1

clean:
    find . -type d -name '__pycache__' -exec rm -rf {} +
    find . -type d -name '.pytest_cache' -exec rm -rf {} +