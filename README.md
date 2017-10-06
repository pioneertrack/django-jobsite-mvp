# BearFounders

Website overview:

 * Django 1.10 web app
 * Basic HTML/CSS/JS (jQuery, Bootstrap)
 * PostgreSQL database
 * Static files hosted on S3, webserver hosted on EC2 (nginx, gunicorn), and data stored on RDS
 * Email backend uses https://sendgrid.com


Admin site can be accessed with the /admin url endpoint

# Views

`connect`: asks for an AJAX POST with `text` and `user` parameters to send the connection email.

`profile`: your profile page

`profile_update`: generates inline form based on whether or not user is founder. If new data is POSTed then write to database.

`get_user_view`: view someone elses profile based on user id in the URL string.

`index`: main page and search logic. The POST received from the search form has the following parameters:

* query - search text
* role
* major
* year
* field
* select-category - startup or people
* startup - has startup exp
* funding - has funding exp

Main search algorithm uses tf-idf ranking based on the query string and the users attributes. First I create the search index as a dictionary of `Key => Words` and `Values => list of [id, [word positions]]`. Using the search index, find all users that correspond to the query. Then rank with tf-idf and return the list.

CSS/JS is a main navbar with a secondary navbar under it. The main nav will hide when the mouse scrolls. Entirely built without data-binding, so just vanilla JS and jQuery.

# Local deployment

1. Clone git repository

2. Install application requirements:

`pip install -r requirements/common.txt`

`pip install -r requirements/prod.txt`

3. Setup your local development environment by copying

`./berkleyconnect/local/local_setting.py` to `./berkleyconnect` directory and adjust settings (DATABASES, EMAIL Settings, etc.) in that file to meet your needs.

4. Create local migrations

`./manage.py makemigrations`

After that apply migrations for database from you local settings

`./manage.py migrate`

5. I add bower support to manage assets libraries. So the nodejs+bower must be installed on the computer. Bower must be installed globally. For install static assets run:

`bower install`

In the root folder for the project
