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

