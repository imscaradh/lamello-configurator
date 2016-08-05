# Lamello Configurator
The purpose of this project is to find out if a given connection is possible with help of Lamello-Connectors. It is build on Django.

## Requirements

The following software should be installed:
* git
* Python 3: https://www.python.org/
* pip: https://pip.pypa.io/en/stable/
* Docker (optional): https://www.docker.com/

To getting started it is recommended to use virutal envorinments for Python. For more information, please read [the documentation](http://docs.python-guide.org/en/latest/dev/virtualenvs/). 

## Installation 

All the following commands are executed on the level of this git repository.

To install all the dependencies for the project, you can install them as the following: 

```bash
pip install -r requirements.txt
```

## Deployment

### Manually
To create the database, run the following commands:

```bash
./manage.py makemigrations
./manage.py migrate
```

Afterwards, you should be able to run the webserver:

```
./manage.py runserver
```

### Aggregated
There is a script which chains all the installation and deployment steps from above. Simply call the script on terminal:
```
./entrypoint.sh
```

## Docker
TODO
