install:
	uv sync

dev:
	uv run python manage.py runserver

migrate:
	uv run python manage.py migrate

collectstatic:
	uv run python manage.py collectstatic --noinput

check:
	uv run python manage.py check

build:
	./build.sh

render-start:
	gunicorn task_manager.wsgi
