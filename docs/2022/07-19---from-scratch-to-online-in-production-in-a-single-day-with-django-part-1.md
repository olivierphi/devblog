---
title: "'From scratch to online in production' in a single day, with Django - Part 1"
date: "2022-07-19"
categories:
  - "webdev"
tags:
  - "django"
  - "project layout"
---

# _'From scratch to online in production'_ in a single day, with Django - Part 1

## A Gin Rummy leaderboard

There is this card game I play _a lot_ with my partner, when we go to the pub or just chill outside: 
[Gin Rummy](https://en.wikipedia.org/wiki/Gin_rummy).

!!! info ":material-cards-playing: If you're curious about the game itself..."
    Gin Rummy is a two-player card game, 
    created by a professional card game player and his son in 1909 - preferably to be played in pubs, as its name made of 2 alcohols' ones hints :slight_smile:
    
    It's easy to learn, the rounds are pretty quick, and even though randomness :game_die: always plays
    an important role in card games its role is not too strong in Gin Rummy.

    :material-lightbulb: A proof of this is that during the 1970s and 1980s there used to be a champion, 
    [Stu Ungar](https://en.wikipedia.org/wiki/Stu_Ungar), 
    who had such a total dominance of the game that it actually ended up killing the game in tournaments, 
    since he was pretty much winning all of them!

In Gin Rummy scoring is easy to determine at the end of each round, however as my partner and I would not keep track 
of our scores from one game to another we noticed that we were playing it more and more casually, 
even a bit too much casually actually :sweat_smile: - which led us to play with less focus
as winning or losing a round had no consequences at this point.    
We like playing casually, but we also like trying to do our best while playing, so we had to find a handy way
to keep track of our scores.

As a Web developer, of course I had to build a leaderboard for us! :nerd: :smile:

## My challenge: start working on it in the morning, and have it live in production in the afternoon

My challenge was to build it in _one single day_, from scratch in the morning to having it online
up and running with a database in the afternoon.  
The stack I'm the most productive with being [Django](https://www.djangoproject.com/),
I opted for this framework despite the minimalism of the project.

!!! note "Is Django a good choice for small projects?"
    Yes! Contrary to frameworks such a Ruby On Rails or Laravel, which tends to create a lot fo files for a blank project,
    creating a new Django project with `django-admin startproject` creates only **6 files**, 
    making it a good choice even for small projects.  
    
    One can even create a Django-powered REST API contained in a single Python file! :star2:
    > https://adamj.eu/tech/2020/10/15/a-single-file-rest-api-in-django/

This is the first post explaining how I typically organise the file tree of a Django project - this layout
does the job for a micro project such as this Gin Rummy leaderboard, but scales very well for 
"real life" projects too!  
I have several Django apps running in production for years with this layout,
and the pattern scales smoothly as features keep being added to the projects :slight_smile:  

Let's start! :zap:

## My typical bootstrap of a Django app

``` bash
$ mkdir gin-scoring && cd gin-scoring/
$ pyenv shell 3.10.4 # (1) 
$ python -m venv .venv # (2)
$ source .venv/bin/activate # (3)
(.venv) $ pip install -U pip poetry # (4)
(.venv) $ poetry init # (5)
(.venv) $ poetry add \ # (6)
    Django \
    django-environ \ # (7)
    psycopg2 \ # (8)
    Jinja2 # (9)
```

1. Let's use a recent version of Python 
2. Create a virtual env in a ".venv" folder
3. Activate the virtual env: from now on the Python-related commands we type only impact the ".venv" folder
4. In the virtual env, update pip and install the Poetry package manager
5. Initialise Poetry for this project
6. Ask Poetry to install the few packages we need for this blog:
7. Install [django-environ](https://django-environ.readthedocs.io/en/latest/) to manage our settings
8. I'll be using Postgresql for the database, so we need a Python driver for it
9. I was never a big fan of the Django built-in templating language, so I always use Jinja instead

!!! note "Installing pip and Poetry in the virtual environment"
    These 2 tools can be used _globally_, and do not require such a local installation.  
    The reason I do this is just because I like having all my Python projects **entirely** self-contained
    in their respective virtual envs.  
    
    So if one of my project uses Poetry 2.x one day, for example,
    I'll be able to use it on new projects without messing up my existing ones :slight_smile:

Once we have this we can bootstrap the project:
``` bash
(.venv) $ mkdir src && cd src/ # (1) 
(.venv) $ django-admin startproject "project" .
```

1. I always put my Python files in a "src/" folder :slight_smile:

With this [startproject](https://docs.djangoproject.com/en/4.0/ref/django-admin/#startproject) command we create 
the skeleton of a Django project in the current folder (`src/`), with a project named "project" - 
I always choose this name because of the way I handle my Django settings.

I like having a `apps/` and a `project/` folders in my `src/` one: the former will be the Python package
where all my Django app code lives, while the latter is where I'll store the project-wide settings.

In a nutshell, the file tree I want to have is this:
``` bash
gin-scoring/
├── src/
│     ├── apps/
│     │     ├── authentication/ # (1) 
│     │     │     ├── migrations/
│     │     │     ├── admin.py
│     │     │     ├── apps.py
│     │     │     └── models.py
│     │     └── gin_scoring/ # (2) 
│     │     │     ├── domain/
│     │     │     ├── jinja2/
│     │     │     ├── migrations/
│     │     │     ├── admin.py
│     │     │     ├── apps.py
│     │     │     ├── helpers.py
│     │     │     ├── http_payloads.py
│     │     │     ├── models.py
│     │     │     └── urls.py
│     ├── project/ # (3) 
│     │     ├── settings/
│     │     │     ├── _base.py # (4) 
│     │     │     ├── development.py
│     │     │     ├── flyio.py
│     │     │     └── heroku.py
│     │     ├── asgi.py # (5)
│     │     ├── jinja2.py
│     │     ├── urls.py
│     │     └── wsgi.py # (6)
│     └── manage.py* # (7)
├── tests/
├── Makefile
├── poetry.lock
└── pyproject.toml
```

1. This will be a `apps.authentication` package
2. This will be a `apps.gin_scoring` package - where the business logic of this mini project will be :-)
3. This is why I use "project" for the name of my Django project when I boostrap it with `django-admin startproject`
4. The "settings" file generated by `django-admin startproject`: I just move it in this folder and rename it into `_base.py`
5. The ASGI (async Python) entry point of the project, generated by Django - I'm not using it at the moment, 
    but it could be useful later on so let's keep it :-)
6. The WSGI ("traditional" Python) entry point: that's where all the HTTP requests of this app will be processed
7. The classic command line entry point for Django - from now on I will always use `python src/manage.py` for my 
    Django commands, and `startproject` was the only one for which I used `django-admin`

_(file tree generated with `tree --dirsfirst -I __pycache__ -F -L 4 . ` - see [tree](https://linux.die.net/man/1/tree)'s MAN page)_

Having all my Django apps namespaced in this `apps` package allows me to use pretty much any name for them,
without any risks of collisions with a 3rd-party package.   

!!! note "Why I namespace my Python code"
    In environments such as PHP or Node.js the 3rd-party packages we add to a project are always namespaced,
    so there are no risks of collisions with our own code.    
    On a Laravel project for example, the HTTP request class will have the fully-qualified name
    `Illuminate\Http\Request`; so we're free to have our own `Request` class with pretty much any prefix we want,
    if we need one in order to follow the "domain" glossary of the project we're building.
    
    However, in the Python world there is not only no namespacing, but also no constrained matching
    between the **name** of a 3rd-party package we add to a project and its Python **package**.  
    For example, the package `django-environ` lives in a package named `environ`.  
    This is why I tend to be a bit defensive when it comes to namespace my own code :sweat_smile:
    
    In that aspect I actually imitate what a typical Laravel project does, since everything is namespaced
    in a top-level `\App\` namespace there:
    > https://laravel.com/docs/9.x/structure#the-app-directory

I can still have collisions in the Django apps names though - but it's a less annoying risk. 

!!! info "Example of a Django apps names collision"
    Django comes with a handy `auth` app that I want to use, which I why I cannot create an app that have this name myself -
    hence my longer `apps.authentication` naming :slight_smile:

## Django settings management

The core of my Django settings are in the file `src/project/settings/_base.py`: this is just the settings file
generated by `django-admin startproject`, that I moved into a new `settings/` folder and renamed - the leading underscore
is just common a convention to emphasise that this Python module shouldn't itself be imported.

### It all starts with a `_base`

The content of this file looks like this:
``` python
import os
from pathlib import Path

import environ

# This points to our git repo's root:
BASE_DIR = Path(__file__).parent.resolve() / ".." / ".." / ".."  

env = environ.Env()
if os.environ.get("USE_DOT_ENV"): # (1)
    for env_file_name in (".env", ".env.local"):
        env_file_path = BASE_DIR / env_file_name
        try:
            environ.Env.read_env(env_file_path)
        except (OSError, AttributeError):
            pass  # no .env file? No problem!

SECRET_KEY = env.str("SECRET_KEY")

# Classic Django settings, generated by `django-admin startproject`
# I'll omit them for brevity
INSTALLED_APPS = [...]

MIDDLEWARE = [...]

ROOT_URLCONF = "project.urls"

# etc.

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": env.db_url("DATABASE_URL"), # (2)
}

# etc., again...
```

1. I will only use this in "local" development: in production the settings are only set via environment variables
2. And here where `django-environ` kicks in again: we use a single `DATABASE_URL` environment var, rather than
    one setting for the username, one for the password, etc.

From there, we just have to define "environment-specific" settings.

### "Local dev" settings

My local development settings look like this for example:
``` python
import os

# This enables the loading of ".env" files in local development:
os.environ["USE_DOT_ENV"] = "YES"

# N.B. This is the only part of my Python code 
# where I allow myself "star imports" :-)
from ._base import * 

DEBUG = True

ALLOWED_HOSTS = []

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env.str("DJANGO_LOG_LEVEL", default="WARNING"),
    },
    "loggers": {
        "apps": {
            "handlers": ["console"],
            "level": env.str("APP_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": env.str("SQL_LOG_LEVEL", default="WARNING"), # (1) 
            "propagate": False,
        },
    },
}
```

1. Such granular logging is very handy in development mode :-)

So if I want to check the SQL queries generated by the Django ORM while I'm working on
the project, all I have to do is to launch my server with:
``` bash
(.venv) $ SQL_LOG_LEVEL=DEBUG djm runserver
```

!!! info "The `djm` shell alias"
    `djm` is short for "DJango Management" - it's an alias I have in my shell's startup file.  
    As I always use this same layout for all my Django projects I can always use
    the same alias to run my Django commands.
    ``` bash
    alias djm='DJANGO_SETTINGS_MODULE=project.settings.development python src/manage.py'
    ```
    
    So from there I can start my Django server with `djm runserver`, generate database migrations
    with `djm makemigrations`, apply them with `djm migrate`, etc.
    
!!! info "The `venv` shell alias"
    Oh, and while we're there, here is another handy alias:
    ``` bash
    alias venv='source .venv/bin/activate'
    ```
    So when I `cd` into a Python project folder I just have to type `venv` to activate its virtual
    environment, as I always create it in a `.venv/` folder :slight_smile:
    

### Production settings

My production (Heroku in this case) settings, in the same folder, look like that:
``` python
from ._base import *

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

DEBUG = False

SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Static assets served by Whitenoise on production
# @link https://devcenter.heroku.com/articles/django-assets
# @link http://whitenoise.evans.io/en/stable/
STATIC_ROOT = BASE_DIR / "staticfiles"
MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
```

In the next post we'll start coding the app itself, using this pattern I was mentioning - which
shines by its simplicity and ability to scale as a project gets more and more complex. :slight_smile:

_Thanks to my friend Yann - [einenlum.com](https://www.einenlum.com/) - for his review on this post :hugging:_
