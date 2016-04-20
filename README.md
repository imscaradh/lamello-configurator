# Lamello Configurator
The purpose of this project is to find out if a given connection is possible with help of Lamello-Connectors. It is build on Django.

## Configuration

To getting started it is recommended to use virutal envorinments for Python. For more information, please read [the documentation](http://docs.python-guide.org/en/latest/dev/virtualenvs/). 

All the following commands are executed on the level of this git repository.

Run the following command to install all required dependencies automatically: 

```bash
pip install -r requirements.txt
```

To create the database, run the following commands:

```bash
./manage.py makemigrations
./manage.py migrate
```

Afterwards, you should be able to run the webserver:

```
./manage.py runserver
```

