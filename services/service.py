import psycopg2
import cherrypy
import json

class Sample(object):

    # Index runs when no web document or "route" is specified
    def index(self):
        return "running!"

    # Runs when /top_x is in the url
    def test(self, x=10):

        # Required for access from external sites.  If you don't have this
        # you may get browser cross-domain scripting security errors. This
        # tells the browser that the server will allow requests to come in
        # from pages originating from another domain.
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

        # Create a database connection
        pgcnxn = psycopg2.connect(host="localhost", database="test", user="postgres", password="quagga")

        # Select statement with cursor
        cursor = pgcnxn.cursor()
        query = "select st_asgeojson(pt), attr from test_table"
        cursor.execute(query)
        rows = cursor.fetchall()

        # For multiple shapes, we need to put them together into a feature collection
        results = { "type": "FeatureCollection",
                    "features": [] }
        for row in rows:
            results["features"].append({ "type": "Feature", "geometry": json.loads(row[0]),
                                         "properties": { "name": row[1]} })

        cursor.close()
        pgcnxn.close()
        return(json.dumps(results))
		
    # These attributes added to the function names tell cherrypy to conver
    # these functions into url routes.
    index.exposed = True
    test.exposed = True
	
cherrypy.config.update({'server.socket_port': 8080})

# This kicks off a bare-bones cherrypy server.  See cherrypy documentation for more startup options.
cherrypy.quickstart(Sample())