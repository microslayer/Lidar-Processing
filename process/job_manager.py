import database as db
import config as conf

def start_available_job():
    # Updates the earliest job from status 0 to status 1, and returns the gis of the updated row. Returns nothing
    # if no pending jobs are available.
    sql = """update job set status = 1
        where gid in (select min(gid) from job where status = 0)
        returning gid"""
    result = None
    current_job = db.exec_sql(sql, [], True)
    if type(current_job) is tuple:
        result = current_job[0]
    return result

def get_tiles_to_process(job_id):
    # Get tiles associated with the given job
    sql = "select tile_id, url from job_tile a inner join tile_index b on a.tile_id = b.gid where a.job_id = %s"
    t = db.get_rows(sql, [job_id])
    results = []
    for d in t:
        results.append({"id": d[0], "url": d[1].replace("\n", "")})
    return results

def update_tile_status(tile_id, status):
    # Returns the status of the tilees in the job, count grouped by status
    sql = "update job_tile set status=%s where tile_id=%s"
    db.exec_sql(sql, [status, tile_id])

def update_job_status(job_id, status):
    # Returns the status of the tilees in the job, count grouped by status
    sql = "update job set status=%s where gid=%s"
    db.exec_sql(sql, [status, job_id])

def add_map_layer(job_id, layer_name, map_url):
    sql = "insert into map_layer (job_id, town_id, name, url) values (%s, (select max(town_id) from job where gid=%s), %s, %s)"
    db.exec_sql(sql, [job_id, job_id, layer_name, map_url])

def complete_job(job_id, town_id, map_url):
    sql = "update job set status = 2 where job_id = %s"
    db.exec_sql(sql, [job_id])
