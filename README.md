Rosie the Robot
---------------

Tracks all of our deploys, so we do need too.

Settings
----------

You will need to configure 2 items in order to launch rosie


*PUPPETDB_SERVER* name of your puppetdb server
*FACT_PREFIX* prefix to all of your custom facts

Facts required
-----------------

rosie will be looking for 3 custom facts in your environment

*<PREFIX><application_name>_deploy_date*
The date of the last time the application was deployed.
This can set my a simple stat of one of the application componets.

*<PREFIX><application_name>_version*
The version of the application that is currently deployed.
Some applications will let you do a simple `--version`.
others you might need to look at a package version of git tag.


Running locally
------------------

	mkvirtualenv rosie
	pip install -U -r requirements.txt
	./main.py

Then just open up http://localhost:5000/ on your machine!
