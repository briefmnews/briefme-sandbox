install:
	pip install -r REQUIREMENTS.txt

runserver:
	python manage.py runserver

migrate:
	python manage.py migrate

reset_db:
	sudo -u postgres psql -c "DROP DATABASE sandbox"
	sudo -u postgres psql -c "CREATE DATABASE sandbox"