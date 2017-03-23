# cs3240 project Spring 2017

## Getting the project running

### Virtual environments:

Create a virtual environment (using conda or virtualenv)

Activate it ```source activate your_env```

### Installing dependencies

Make sure pip is installed in the environment (may have to do ```conda install pip```)

In the root folder of the project do ```pip install -r requirements.txt```

### Setting up the database

Run ```python manage.py migrate```

### Finally

```python manage.py runserver```

## Managing through the admin interface

Run the command ```python manage.py createsuperuser``` to make yourself a superuser account

Go to /admin and log in with the superuser account to manage users

## Creating new models, modifying models

Create new models or make modifcations to existing models. Then run '''manage.py makemigrations'''

Then use ```manage.py migrate``` to apply the migrations




