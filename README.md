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
    + Django-dotenv
- HTML/CSS
- JavaScript
    + jQuery

# Installation

> **NOTE!** If you're new to Django, or simply not used to setting up someone else's project for your use, I highly recommend looking at the more detailed instructions in the [Setup](https://github.com/TaijaQ/Kudryavka/wiki/Setup) wiki page.

First clone the project locally using git.

    $ git clone git@github.com:TaijaQ/Kudryavka.git

I recommend creating a virtual environment using `virtualenvwrapper`. This command creates the environment and installs the packages in the `requirements.txt` file:

    $ mkvirtualenv -r requirements.txt env_name

Next create the Postgres database and add the database name, user and password to the settings. Then migrate it:

    (env_name) $ ./manage.py migrate

## Configuration

There are a few envirnoment variables needed in the settings. The `django-dotenv` package supplies an implementation of `dotenv` for django. Create a file named `.env` in the project folder and add these lines to it, with your own information:

    SECRET_KEY='your_secret_key'
    ACCESS_TOKEN=''
    DEBUG=True
    DATABASE_USER='user'
    DATABASE_NAME='name'
    USER_PASSWORD='password'
    TIME_ZONE='Europe/Helsinki'

Since you don't ever run `django-admin startproject`, which will automatically add a randomly-generated `SECRET_KEY` to a project, you can get one with [MiniWebTool's generator](http://www.miniwebtool.com/django-secret-key-generator/).

>**NOTE!** Remember to add `.env` to your `.gitignore` file - don't commit it.

## Running the server

Now just create a superuser with Django and you should be ready to go. In the project folder, run:

    $ ./manage.py runserver

Now you can visit the URL `http://127.0.0.1:8000/`, where you should see the Kudryavka project.

Up in the corner, there's the `ADMIN` link which will take you straight to the admin page (you can login with the superuser account). I recommend adding some project categories, projects and posts there first so you can see how the data looks on the main site.