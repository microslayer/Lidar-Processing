## Lidar-Processing

Code to generate map layers from airborne lidar and display them in web maps.

## Directory structure

/site - Static web site files  

/site/js

/site/css

/site/img

/site/lib/js -- leaflet, bootstrap, jquery, etc.

/site/lib/css -- related css files

/services - Cherrypy web service python files - would live on a python web server with a DB connection

/process - batch process python files - may be distributed among worker machines

/db - Database scripts - postgres table definitions, stored procedure code, etc.

/docs - Notes and documentation

/misc - Experiments, test code, scratch files.
