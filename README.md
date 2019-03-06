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
python manage.py loaddata sample-data
```

Note that the last step loads some sample data from the fixture sample-data.json.

This also creates an admin user admin@mail.com with password pass1234

Run app:

```
python manage.py runserver
```

Navigate to http://localhost:8000/, or http://localhost:8000/admin and login as the admin user (admin@mail.com/pass1234).

## Deploying on Heroku

Here are some useful heroku commands:

```
git commit --allow-empty -m "Trigger Heroku deploy"
git push heroku master

heroku pg:reset DATABASE
heroku run rake db:migrate

```

