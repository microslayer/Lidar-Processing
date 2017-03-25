import psycopg2  as pg
import config as conf

def get_new_job_id(town_id):
    # Gets a new job identifier if the town has not yet been processed
    cnxn = pg.connect(host=conf.db["host"], database=conf.db["database"], user=conf.db["user"], password=conf.db["password"])
    cursor = cnxn.cursor()
    job_id = (-1,)
    try:
        sql = "select count(*) from map_layer where town_id = %s"
        cursor.execute(sql, (town_id,))
        existing_rows = cursor.fetchone()
        if existing_rows[0] > 0:
            raise(Exception("This town has already been processed!  Please view available map layers instead"))
        sql = "select nextval('job_gid_seq')"
        cursor = cnxn.cursor()
        cursor.execute(sql)
        job_id = cursor.fetchone()
    finally:
        cursor.close()
        cnxn.close()
    return str(job_id[0])

def get_tile_list(town_id):
    sql = """select a.gid from tile_index a inner join us_town b on st_intersects (a.geom, b.geom) where b.gid = %s"""
    cnxn = pg.connect(host=conf.db["host"], database=conf.db["database"], user=conf.db["user"], password=conf.db["password"])
    cursor = cnxn.cursor()
    cursor.execute(sql, (town_id,))
    results = []
    for row in cursor.fetchall():
        results.append(row[0])
    cursor.close()
    cnxn.close()
    return results

def start_job(job_id, town_id, tile_list):
    # Starts a job by inserting rows into job and job_tile table
    params = []
    for t in tile_list:
        params.append((job_id, t, 0))
    cnxn = pg.connect(host=conf.db["host"], database=conf.db["database"], user=conf.db["user"], password=conf.db["password"])
    cursor = cnxn.cursor()
    # Create the parent job record
    cursor.execute("insert into job (gid, town_id, status) values (%s, %s, 0)", (job_id, town_id))
    # Create the tile records
    sql = "insert into job_tile(job_id, tile_id, status) values(%s, %s, %s)"
    cursor.executemany(sql, params)
    cursor.close()
    cnxn.commit()
    cnxn.close()

def cancel_job(job_id):
    # Deletes the job, causing it to be cancelled
    cnxn = pg.connect(host=conf.db["host"], database=conf.db["database"], user=conf.db["user"], password=conf.db["password"])
    cursor = cnxn.cursor()
    cursor.execute("delete from job_tile where job_id = %s", (job_id,))
    cursor.execute("delete from job where gid=%s", (job_id,))
    cursor.close()
    cnxn.commit()
    cnxn.close()

def job_status(job_id):
    # Returns the status of the tilees in the job, count grouped by status
    sql = "select status from job where gid = %s"
    result = -1
    cnxn = pg.connect(host=conf.db["host"], database=conf.db["database"], user=conf.db["user"], password=conf.db["password"])
    cursor = cnxn.cursor()
    cursor.execute(sql, (job_id,))
    result = cursor.fetchone()[0]
    cursor.close()
    cnxn.close()
    return result

def fetch_tile_list(lat, lon):

    cnxn = None
    #  locate town containing coordinate
    sql = """SELECT ST_ASTEXT(geom)
             FROM us_town
             WHERE ST_Contains(geom, st_geomfromtext('POINT({0} {1} )', 4326))""".format(str(lon), str(lat))

    try:

        cnxn = pg.connect(host=conf.db["host"], database=conf.db["database"], user=conf.db["user"], password=conf.db["password"])
        cursor = cnxn.cursor()
        cursor.execute(sql)

        # find the tiles that are within the town corresponding to the coordinate
        sql = """ SELECT index
                  FROM  tile_index
                  WHERE ST_Within(geom, st_geomfromtext('{0}',4326))""".format(cursor.fetchone()[0])
        cursor.execute(sql)

        # return the tile indices
        results = []
        for row in cursor.fetchall():
            results.append(row[0])
        cursor.close()
        return results
    except (Exception, pg.DatabaseError) as error:
        return error
    finally:
        if cnxn is not None:
            cnxn.close()




