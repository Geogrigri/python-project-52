install:
	uv sync

dev:
	uv run python manage.py runserver

migrate:
	uv run python manage.py migrate

check:
	uv run python manage.py check
