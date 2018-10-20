# Atria Calendar

Event scheduling and volunteer management platform

## Environment Setup

```
cd atria-calendar
virtualenv --python=python3.6 venv
source venv/bin/activate
```

## Install and run atria calendar

Install dependencies:

```
cd atriaapp
pip install -r requirements/demo.txt
```

Build app:

```
cd atria-calendar/atriaaapp
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

Run app:

```
python manage.py runserver
```

Navigate to http://localhost:8000/, or http://localhost:8000/admin and login as the admin user (created by "createsuperuser" above).
