pollsite
========

This is a reimplementation of the [Django Pollsite Tutorial](https://docs.djangoproject.com/en/1.8/intro/tutorial01/) for beginners with a substantial number of changes and improvements.  These include:

* Added Bootstrap styling
* Added user registration and login functionality
* Converted function-based views to Class-based views
* Added extra unit tests and test data
* Added charts to visualize poll results
* Added functionality allowing users to create polls without going through the admin pane
* Added the concept of a "Vote" so that users can only vote once on each question
* Added the concept of an "author" to the Question model so that users know which questions they have created

This is my first foray into Django development.  While this code is my own work, it is important to note that I started with code provided by the [Django Project](https://www.djangoproject.com/) and rewrote it as needed to make the improvements I listed above.  