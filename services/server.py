import cherrypy
import json
import batch_process as bp
import config as conf
import traceback as tb

class Server(object):
    stub_mode = True
    # --------------------------------------------------------------------------------
    # Utility functions for CherryPy endpoints
    # --------------------------------------------------------------------------------

    def get_response_wrapper(self):
        # Gets a wrapper for service reponses
        return {
            "status": 200,
            "data": dict(),
            "message": "Success"
        }

    def set_response_headers(self):
        # Sets the response headers to url can be accessed from any web site, and so the browser recognizes the content
        # as json text.
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        cherrypy.response.headers['Content-Type'] = 'application/json'

    def encode_results(self, result):
        self.set_response_headers()
        return json.dumps(result).encode('utf-8')

    @cherrypy.expose
    def index(self):
        # Index runs when no web document or "route" is specified
        return self.encode_results("running!")

    # --------------------------------------------------------------------------------
    # Batch job endpoints for starting, querying, and cancelling jobs from the
    # web interface
    # --------------------------------------------------------------------------------

    @cherrypy.expose
    def start_job(self, town_id):
        # Example: http://localhost:8080/start_job?town_id=11850
        # Assigns a batch id, starts it off, and returns the job id to the client.
        result = self.get_response_wrapper()
        try:
            if Server.stub_mode:
                result["data"]["job_id"] = 100
                result["data"]["num_tiles"] = 32
            else:
                job_id = bp.get_new_job_id(town_id)
                tile_list = bp.get_tile_list(town_id)
                bp.start_job(job_id, town_id, tile_list)
                result["data"]["job_id"] = job_id
                result["data"]["num_tiles"] = len(tile_list)
        except Exception as e:
            result["status"] = 500
            result["message"] = "{0} {1}".format(e, tb.format_exc())
        return self.encode_results(result)

    @cherrypy.expose
    def job_status(self, job_id):
        # Gets the status of the job.
        # Example: http://localhost:8080/job_status?job_id=42
        result = self.get_response_wrapper()
        try:
            if Server.stub_mode:
                result["data"]["description"] = "Downloading files"
                result["data"]["stage"] = "1 of 5"
                result["data"]["percent_done"] = 10
            else:
                stage = bp.job_status(job_id)
                # TODO - convert from stage number to text
                result["data"]["description"] = "Downloading files"
                result["data"]["stage"] = "{0} of 5".format(stage)
                result["data"]["percent_done"] = stage * 20
        except Exception as e:
            result["status"] = 500
            result["message"] = "{0} {1}".format(e, tb.format_exc())
        return self.encode_results(result)

    @cherrypy.expose
    def cancel_job(self, job_id):
        # Cancels the job.
        # Example: http://localhost:8080/cancel_job?job_id=45
        result = self.get_response_wrapper()
        try:
            if Server.stub_mode:
                result["data"]["description"] = "Job cancelled"
            else:
                bp.cancel_job(job_id)
                result["data"]["description"] = "Job cancelled"
        except Exception as e:
            result["status"] = 500
            result["message"] = "{0} {1}".format(e, tb.format_exc())
        return self.encode_results(result)

    @cherrypy.expose
    def completed_jobs(self):
        # Cancels the job.
        # Example: http://localhost:8080/completed_jobs
        result = self.get_response_wrapper()
        try:
            if Server.stub_mode:
                result["data"] = [
                    {
                        "name": "Northampton, MA",
                        "town_id": 11850,
                        "job_id": 45
                    },
                    {
                        "name": "Scranton, PA",
                        "town_id": 28369,
                        "job_id": 46
                    },
                ]
            else:
                # TODO: update with db query of jobs and towns tables
                pass
        except Exception as e:
            result["status"] = 500
            result["message"] = "{0} {1}".format(e, tb.format_exc())
        return self.encode_results(result)

    @cherrypy.expose
    def layers_in_job(self, job_id):
        # Cancels the job.
        # Example: http://localhost:8080/layers_in_job?job_id=45
        result = self.get_response_wrapper()
        try:
            if Server.stub_mode:
                result["data"] = [
                    {
                        "name": "Digital Surface Model",
                        "url": "/45_dsm"
                    },
                    {
                        "name": "Digital Elevation Model",
                        "url": "/45_dem"
                    },
                    {
                        "name": "Height Model",
                        "url": "/45_ndsm"
                    },
                    {
                        "name": "Solar Radiation",
                        "url": "/45_sol"
                    },
                    {
                        "name": "Tree Cover",
                        "url": "/45_tree"
                    },
                ]
            else:
                # TODO: update with db query of jobs and map_layers tables
                pass
        except Exception as e:
            result["status"] = 500
            result["message"] = "{0} {1}".format(e, tb.format_exc())
        return self.encode_results(result)

    # --------------------------------------------------------------------------------
    # Other endpoints as needed - don't put too much here so this file doesn't get
    # too huge - most of the work can be done in external modules.
    # --------------------------------------------------------------------------------

    @cherrypy.expose
    def example(self, lat, lon):
        # Example endpoint, accessible via:
        # http://localhost:8080/example?param1=test1&param2=test2
        result = self.get_response_wrapper()
        result["data"] = [lat, lon]
        return self.encode_results(result)

# This should usually be the main entry point of the service application, so __name__ should equal "__main__"
if __name__ == '__main__':
    # Set up site-wide config first so we get a log if errors occur.
    cherrypy.config.update({'environment': 'production',
                        'log.access_file': None,  # 'site.log',
                        'log.screen': True,
                        'server.thread_pool': 10,
                        'server.socket_host': '0.0.0.0',
                        'tools.encode.on': True,
                        'tools.encode.encoding': 'utf-8',
                        'server.socket_port': conf.port})
    # CherryPy creates an instance of the server object, then spins up multiple threads to access that server.
    cherrypy.quickstart(Server())