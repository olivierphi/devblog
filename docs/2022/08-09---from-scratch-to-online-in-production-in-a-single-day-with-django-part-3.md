---
title: "'From scratch to online in production' in a single day, with Django - Part 3"
date: "2022-08-09"
categories:
  - "webdev"
tags:
  - "django"
  - "deployment"
---

# _'From scratch to online in production'_ in a single day, with Django - Part 3

## Prototype is working, now it's time to deploy it

In [part 1](/2022/07-19---from-scratch-to-online-in-production-in-a-single-day-with-django-part-1) we saw
a way to set up a Django project in a quite generic way, that can be used for _any_ kind of project.

In [part 2](/2022/07-22---from-scratch-to-online-in-production-in-a-single-day-with-django-part-2) I explained
a bit how I structure my Django projects, based on HackSoft's
[Django Styleguide](https://github.com/HackSoftware/Django-Styleguide#services) with just a slight personal deviation on top of it.

After this I quickly set up an HTML/CSS user interface, rendered by Jinja templates 
and powered by the [Bulma](https://bulma.io/) CSS framework - which is quite good for rapid prototyping.   

After a few quick tests I had a working prototype around 4pm :clock4:, for this project started the same day at 9am.  
Which means I had about one more hour to deploy it to production to meet my goal! :sweat_smile:    
_*rolling up his sleeves for the home straight_

## Deploying a Django app to Heroku, with a free plan

[Heroku](https://www.heroku.com/) no longer has the great reputation it used to have back in the days, but I still like it
and tend to still choose it as my primary deployment target in my commercial projects, as it still comes with some really strong benefits:

 - Deploying a project is just a matter of doing `git push` to the Heroku git remote
 - Rolling back to a previous version is just a click on their dashboard - or a command with their CLI client
 - Postgres and Redis are builtin and fully managed
 - [Review Apps](https://devcenter.heroku.com/articles/github-integration-review-apps) are still pretty amazing :sparkles: : a push
    to a branch (or the creation of a PR) automatically spawns a new environment for this branch, with its own database - that
    will be destroyed automatically when we're no longer using it.  
    This really is a critical feature to me, as it allow project managers to test a new feature or a bugfix before it's merged,
    without having to spend days and days setting up and maintaining such a process manually.

It's possible to deploy Docker images, but one can also rely on open source [buildpacks](https://elements.heroku.com/buildpacks),
which are basically pre-configured setup scripts that install the software we need for a given stack. There are buildpacks
for Python, Node.js, Ruby, Go, PHP, Java...  
Buildpacks can have framework-specific steps, such as running the [collectstatic](https://docs.djangoproject.com/en/4.1/howto/static-files/deployment/) 
Django command automatically if Django is detected in the project :ok_hand:

However, the fact that I'm using Poetry to manage my Python dependencies is an edge case that the Python buildpack doesn't
handle, so we have to use a trick to make this work :sweat_smile:

### Deploying a Poetry-powered Python project to Heroku

A few years ago I had the need to add some custom steps to the deployment of a Django project, and by inspecting the source
code of the Python buildpack I found this in [the compilation script](https://github.com/heroku/heroku-buildpack-python/blob/main/bin/compile):

``` shell
# Experimental post_compile hook. Don't remove this.
source "$BIN_DIR/steps/hooks/post_compile"
```

...which in turns triggers [this script](https://github.com/heroku/heroku-buildpack-python/blob/main/bin/steps/hooks/post_compile):

``` shell
if [ -f bin/post_compile ]; then
    echo "-----> Running post-compile hook"
    chmod +x bin/post_compile
    sub_env bin/post_compile
fi
```

Right, so if there is a `bin/post_compile` file in the git repository it will be executed by Heroku after its own
"compilation" step...  
That sounds like a good target for my custom deployment steps! :slight_smile:

### My `bin/post_compile` script

Here is the quick Bash script I made a few years ago, and that I've been copy-pasting from project to project since
when I deploy them to Heroku:

``` shell
#!/bin/bash
# file: /bin/post_compile

# Heroku "hidden" post-compilation hook 
# (had to dig into the Heroku Python build pack source code to find that :-)
set -eo pipefail
echo '**** CUSTOM HEROKU PYTHON BUILD PACK "bin/post_compile" HOOK'

indent() {
  sed "s/^/       /"
}

puts-step() {
  echo "-----> $@"
}

puts-step "Installing dependencies with Poetry..."
poetry config virtualenvs.create false 2>&1 | indent
poetry install --no-dev 2>&1 | indent

puts-step "Collecting static files, now that Whitenoise is installed..."
python src/manage.py collectstatic --no-input 2>&1 | indent

# Any other custom step can go here :-)
```

So in this script I simply add a custom step where I install my dependencies with Poetry,
and once it's done I trigger the `collectstatic` Django command.  
It's easy then to add other custom steps to this script, depending on the project.

To get this work we only need to do these 2 things beforehand: :octicons-checklist-24:

 - Still have a root `requirements.txt` file - so that Heroku automatically recognises a Python project -
    and specify one single dependency there: Poetry itself.
   ``` shell
    # file: /requirements.txt
    # This is only required to satisfy Heroku's Python build pack, 
    # which doesn't handle Poetry (yet?).
    # The real dependencies install will happen in the "bin/post_compile" file.
    poetry==1.1.13    
   ```
 - Ask the buildpack to not try to run `collectstatic` itself in its own compilation script: in production we serve
    our static assets with [WhiteNoise](http://whitenoise.evans.io/en/stable/), but this package is installed with Poetry
    later on in our `bin/post_compile` script and would not be found at the time when the builtin compilation script is triggered.   
    Thankfully, the buildpack's documentation explains [how to opt-out from this compilation step](https://devcenter.heroku.com/articles/django-assets#disabling-collectstatic),
    simply by setting the `DISABLE_COLLECTSTATIC` environment variable.  
    Which can be made via the Web dashboard or the Heroku CLI:
   ``` shell
   heroku config:set DISABLE_COLLECTSTATIC=1
   ``` 

###  Limitations of the Heroku free plan

As every free plan, Heroku's one come with some limitations.

 - The Postgres database is limited to 10,000 max rows, 1GB max storage and 20 connections at a time
    (details [here](https://elements.heroku.com/addons/heroku-postgresql)).  
   For this "Gin Rummy leaderboard" these limits are not a problem :slight_smile:
 - The app itself is put into "sleep" after 30 minutes of inactivity, and waking it up typically takes a few seconds.  
    That's obviously a very annoying restriction for "real" projects :sweat_smile:  
    However, in this case this is just a simple Web page that will only record the Gin Rummy scores of the games I play with my partner,
    so having to wait a few sec for recording the first score when we start to play a few rounds is not a big deal.

With real commercial projects I tend to start with the free plan, so project managers can start using the project
as soon as possible - and we migrate to paid plans only when we need to.

##  Using the app

By picking Heroku, a platform I'm familiar with, I was able to have this "Gin Rummy leaderboard" Django app online in production
around 5pm; we started to record our first scores there an hour later when we met at the pub. :beers:  
I typed `django-admin startproject` at 9am, and used the project in production at 6pm - challenge accomplished!   
...and it was really fun to give myself this constraint :slight_smile:

##  Addendum: deployment to Fly.io

Out of curiosity, a few days later I also implemented the deployment of the Django project to [Fly.io](https://fly.io/) - which is a platform I
wanted to try for a while.

I just had to create a Dockerfile for my app, and then follow [their documentation](https://fly.io/docs/getting-started/python/)
to deploy my Docker image to their infrastructure and [link a Postgres database](https://fly.io/docs/reference/postgres/) to it.  
Despite the fact that it was the very first time I was using it, one hour later I had my instance running - which tells
how straightforward deploying an app to Fly.io is! :slight_smile: 

My quick `fly.toml` file looks like this:
``` toml
app = "[the name of my app]"
kill_signal = "SIGINT"
kill_timeout = 5
processes = []

[env]
  PORT = "8080"
  DJANGO_SETTINGS_MODULE = "project.settings.flyio"

[[services]]
  internal_port = 8080
  processes = ["app"]
  protocol = "tcp"
  script_checks = []

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.http_checks]]
    interval = 15000
    grace_period = "5s"
    method = "get"
    path = "/"
    protocol = "https"
    restart_limit = 0
    timeout = 1000
    tls_skip_verify = false

[[statics]]
  guest_path = "/app/staticfiles"
  url_prefix = "/static/"
```

And contrary to Heroku, the app doesn't sleep after 30 minutes of inactivity. :ok_hand:  
The only downside is that although I'm using [their free allowance](https://fly.io/docs/about/pricing/#trial-plan) I had to give my credit card :credit_card: detail
to Fly.io before being able to deploy my first app - which is not the case with Heroku.

###  My quick "Django project" Dockerfile

There are plenty of resources on the Web to create fine-tuned Dockerfiles for a Django project, but here is the one
I quickly set up to deploy this side project to Fly.io:

``` Dockerfile
ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION} AS build

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN mkdir -p /app
WORKDIR /app

RUN python -m venv .venv

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

FROM python:${PYTHON_VERSION}-slim AS run

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app
WORKDIR /app

RUN addgroup -gid 1001 webapp
RUN useradd --gid 1001 --uid 1001 webapp
RUN chown -R 1001:1001 /app 
USER 1001:1001

COPY --chown=1001:1001 --from=build /app/.venv .venv
COPY --chown=1001:1001 . .

ENV PYTHONPATH=/app/src

RUN SECRET_KEY=does-not-matter-for-this-command DATABASE_URL=sqlite://:memory: ALLOWED_HOSTS=fly.io \
    .venv/bin/python src/manage.py collectstatic --noinput

EXPOSE 8080

CMD [".venv/bin/gunicorn", "--bind", ":8080", "--workers", "2", "project.wsgi"]
```

There is of course room for a lot of improvement there, but this quick multi-stage Dockerfile
creates a 220MB image which is not too bad :slight_smile:
