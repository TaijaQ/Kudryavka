
=================
KUDRYAVKA
=================

Kudryavka is a project management application based on the Django framework. Orgmode as my inspiration and I use django.mptt to manage the hierarchail data.

This is a work in progress. My plan is to add inline editing in the notebooks, a seperate archive and an agenda view, based on the TODOs.


Installation
============

First, clone my project locally and make sure you have Python installed. I use virtualenvwrapper to create a virtual environment for the project, you can install it with pip:

    $ pip install virtualenvwrapper

Then create a new environment for your project in its directory, using the requirements file in my project to also automatically install the packages.

    $ mkvirtualenv -r requirements.txt project_name
    $ workon project_name

If you want to install the required packages by hand, they are as follows:

    Django==1.9.7
    django-jquery==1.12.2
    django-mptt==0.8.6
    parsedatetime==2.1
    psycopg2==2.6.2
    pytz==2016.4

To stop working in the environment, you simply use:

    $ deactivate

Now you can create your django project.

    $ django-admin startproject mysite


Configuration
=============

We'll need to configure your settings before we can get to work. There are a few envirnoment variables used in the production settings. If you want to manually input the information, you can do that, or add the variables to the end of your virtualenv activation script. Run:

    $ nano $VIRTUAL_ENV/bin/activate 

And add the variables to the end of the file:

    export SECRET_KEY='your_secret_key'
    export DEBUG=True
    export DATABASE_USER='user'
    export DATABASE_NAME='name'
    export DATABASE_PASSWORD='password'
    export TIME_ZONE='Europe/Helsinki'

Then create a Postgres database with the same name and right user privilidges. 

You should either change the name of the ``production_settings.py`` file to ``settings.py``, or run the server with the option ``--settings=project.production_settings.py``

Now, just create a superuser with Django and you should be ready to go. In the project folder, run:

    $ ./manage.py runserver


And now you can start adding some data!


Features
========

- Project management
- Orgmode-style notes and todos for projects, collectively called posts
    + States and priorities for todos
    + Links that are applied automatically
    + Tags
- Project views
- Hierarchy using Django MPTT
    + Hierarchial admin view
    + Hierarchial, stylized project view
- Custom datetime fields
    + Can handle timezones and local time, and deal with aware/naive datetimes


TODO
====

- [ ] Ability to add new posts from the project view
- [ ] Inline editing and moving of nodes in the project view
- [ ] Overall agenda view
- [ ] Project-based agenda view
- [ ] Progress
- [ ] A working archive
- [ ] Filtering posts by tag, priority etc.