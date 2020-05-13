# Briefme Sandbox

## Installation
* Create a postgres database (version 9.6) named `sandbox` with username `briefme` and password `briefme`.
* Create a virtual environment with python 3.7.
* Run the command `make install` to install all the dependencies.
* Then run `make reset_db`. The project includes fixtures with dummy data (`./fixtures/fixtures.sql`)
* Finally run `make runserver` and open a browser on `http://localhost::8000`.

You can connect to the admin with the url `http://localhost:8000/admin`. A super user already
exists with the username `briefme` and the password `briefme`.