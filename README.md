# KUDRYAVKA

Kudryavka is a hierarchial project management application built on the Django framework. Orgmode is my inspiration and I use django.mptt to manage the hierarchial data.

This is a work in progress. My plan is to add inline editing in the notebooks, a seperate archive and an agenda view.  See the [Development](https://github.com/TaijaQ/Kudryavka/wiki/Development) wiki page for more information.

## Table of contents

<!-- MarkdownTOC -->

- [Features](#features)
- [Technology](#technology)
- [Installation](#installation)
    - [Configuration](#configuration)
    - [Running the server](#running-the-server)

<!-- /MarkdownTOC -->

# Features

- Projects and subprojects
- Orgmode-style notebooks
    + Notes
    + Todos
        * States and priorities for todos
    + Links that are applied automatically
    + Tags
- Agenda
- Archive
- Hierarchy using Django MPTT
    + Hierarchial admin view
    + Hierarchial, stylized project view
- Custom datetime fields
    + Can handle timezones and local time, and deal with aware/naive datetimes
- Admin page
    + Hierarchial admin views (Tags, Projects)
    + Draggable (Tags, Projects)

# Technology

- Python
    + Django framework
- Postgres database
    + Psycopg2
- Extensions
    + Pytz
    + Django-mptt
- HTML/CSS
- JavaScript
    + jQuery

# Installation

If you're new to Django, I highly recommend looking at the detailed instructions in the [Setup](https://github.com/TaijaQ/Kudryavka/wiki/Setup) wiki page.

First clone the project locally.

    $ git clone git@github.com:TaijaQ/Kudryavka.git

I recommend creating a virtual environment using virtualenvwrapper. This creates the environment and installs the packages in the `requirements.txt` file:

    $ mkvirtualenv -r requirements.txt env_name

Next create the Postgres database and add the database name, user and password to the settings, and run:

    (env) $ ./manage.py migrate

## Configuration

We'll need to configure your settings before we can get to work. There are a few envirnoment variables used in the production settings. Run:

    (env) $ nano secrets.sh

Then add these lines to it:

    export SECRET_KEY='your_secret_key'
    export ACCESS_TOKEN=''
    export DEBUG=True
    export DATABASE_USER='user'
    export DATABASE_NAME='name'
    export USER_PASSWORD='password'
    export TIME_ZONE='Europe/Helsinki'

Replacing the variables with your own information. Since you don't ever run `django-admin startproject`, which will automatically add a randomly-generated `SECRET_KEY` to a project, you can get one with [MiniWebTool's generator](http://www.miniwebtool.com/django-secret-key-generator/).

After that, you will need to to load the variables into every terminal session with the command:

    (env) $ source secrets.sh

**NOTE!**
Remember to add `secrets.sh` to your `.gitignore` file.

## Running the server

Now just create a superuser with Django and you should be ready to go. In the project folder, run:

    $ ./manage.py runserver

Now you can visit the URL `http://127.0.0.1:8000/`, where you should see the Kudryavka project.

Up in the corner, there's the `ADMIN` link which will take you straight to the admin page (you can login with the superuser account). I recommend adding some project categories, projects and posts there first so you can see how the data looks on the main site.