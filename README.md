## Lidar-Processing

Code to generate map layers from airborne lidar and display them in web maps.

## Directory structure

/site - Static web site files - you can start a web server over port 8000 that uses this directory as its root by opening a command line, navigating to this directory, and typing "python -m http.server"

/site/js

/site/css

/site/img

/site/lib/js -- leaflet, bootstrap, jquery, etc.

/site/lib/css -- related css files

/services - Cherrypy web service python files - would live on a python web server with a DB connection. To start the server that runs the services over port 8080, open up a command line window, navigate to this directory, and type "python server.py"

/process - batch process python files - may be distributed among worker machines

/db - Database scripts - postgres table definitions, stored procedure code, etc.

/docs - Notes and documentation

/misc - Experiments, test code, scratch files.
