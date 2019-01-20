from .settings import *

ALLOWED_HOSTS.extend(
    ['cryptic-forest-87771.herokuapp.com', '127.0.0.1', 'localhost'])

django_heroku.settings(locals())
