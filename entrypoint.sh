(cd configurator; django-admin compilemessages)
python manage.py makemigrations
python manage.py makemigrations configurator
python manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('superuser', '', 'superuser')" | python manage.py shell
python manage.py runserver 0.0.0.0:8000
