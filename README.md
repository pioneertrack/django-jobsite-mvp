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

`get_user_view`: view someone else's profile based on user id in the URL string.

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

3. Set up your local development environment by copying

`./berkeleyconnect/local/local_settings.py` to the `./berkeleyconnect` directory.

> a.If you want to use `localhost` rather than `127`, change the line to ```ALLOWED_HOSTS = ['127.0.0.1', 'localhost']```  
>
> b.  Set up a PostgreSQL server on your local machine and update the `DATABASE` settings to reflect this.  
>
> c.  If you want to be able to send emails from your local server (this is only one way to do this):  
>>   i.  Change your email host to `smtp.gmail.com` and your port to `587`.  
>>   ii.  Choose a valid email address you'd like to send from. Set up Google Two-Step Verification if you don't already have it, and generate an app password.  
>>  iii.  Change `EMAIL_HOST_USER` and set the password to the App Password you generated. Two-Step Verification does not need to remain on after you do this.  
>>   iv.  Change `EMAIL_USE_TLS` to `True`.  
>
> d.  If you want to be able to receive emails as an admin from your local server:  
>>   i.  Ensure that you followed steps in part C to establish an address will be able to send emails.  
>>   ii.  Choose the email address you want to use for receiving emails. Note this doesn't need to be a valid email address, but it might be useful depending on what you're working on.  
>>   ii.  Change `DEFAULT_FEEDBACK_EMAIL` to the receiving email address.  
>
> e. Set the `TEST_EMAIL` variable so you don't accidentally send emails to end users by accident.  
>
> f.  Set up `elasticsearch` if you don't already have it.  

4. Apply migrations for database from your local settings

`./manage.py migrate`

5. I add bower support to manage assets libraries. So the nodejs+bower must be installed on the computer. Bower must be installed globally. For install static assets run:

`bower install`

In the root folder for the project

6. 2017/11/28 Bower support for bootstrap 4 was ended so I start to fully move assets management under npm. 
Therefore now for normal functioning it is necessary to execute the command 

`npm install`

in common with

`bower install`

to fully set up assets environment. 

Must have elasticsearch downloaded and run the `elasticsearch` command to set up the elasticsearch server before using `python manage.py runserver`.

The pages for startups, jobs, and members may start off giving you a 404 error. If this is the case, you must create a startup, job, and member on your local server. This can be done in the admin site at `/admin/`, or you could create a local member profile, use that profile to create a startup, and use that startup to offer a job.
