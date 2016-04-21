(cd configurator; django-admin compilemessages)
python manage.py makemigrations
python manage.py makemigrations configurator
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
