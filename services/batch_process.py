import uuid
import psycopg2  as pg
import config as conf

def get_new_job_id():
    # Gets a new job identifier
    job_id = uuid.uuid4()
    return str(job_id)

def get_tile_list(lat, lon):
    # Gets a list of tiles to process
    # TODO: replace with query to towns and tiles table.
    results = ["https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/50002560_50002560_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/50002550_50002550_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/50002540_50002540_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/50002530_50002530_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/50002520_50002520_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/49002560_49002560_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/49002550_49002550_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/49002540_49002540_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/49002530_49002530_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/49002520_49002520_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/48002560_48002560_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/48002550_48002550_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/48002540_48002540_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/48002530_48002530_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/48002520_48002520_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/47002560_47002560_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/47002550_47002550_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/47002540_47002540_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/47002530_47002530_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/47002520_47002520_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/46002560_46002560_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/46002550_46002550_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/46002540_46002540_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/46002530_46002530_pa_north06.laz",
               "https://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/2573/46002520_46002520_pa_north06.laz"]
    return results

def start_job(job_id, tile_list):
    # Starts a job by inserting rows into batch table
    # TODO - need to assign jobs an id that will be repeated if another user tries to process the same town!
    sql = "insert into batch_tile(job_id, tile_url, status) values(%s, %s, %s)"
    params = []
    for t in tile_list:
        params.append((job_id, t, 0))
    cnxn = pg.connect(host=conf.db["host"], database=conf.db["database"], user=conf.db["user"], password=conf.db["password"])
    cursor = cnxn.cursor()
    cursor.executemany(sql, params)
    cursor.close()
    cnxn.commit()
    cnxn.close()

def cancel_job(job_id):
    # Deletes the job, causing it to be cancelled
    sql = "delete from batch_tile where job_id = %s"
    cnxn = pg.connect(host=conf.db["host"], database=conf.db["database"], user=conf.db["user"], password=conf.db["password"])
    cursor = cnxn.cursor()
    cursor.execute(sql, (job_id,))
    cursor.close()
    cnxn.commit()
    cnxn.close()

def job_status(job_id):
    # Returns the status of the tilees in the job, count grouped by status
    sql = "select status, count(*) from batch_tile where job_id = %s group by status order by status asc"
    results = {}
    cnxn = pg.connect(host=conf.db["host"], database=conf.db["database"], user=conf.db["user"], password=conf.db["password"])
    cursor = cnxn.cursor()
    cursor.execute(sql, (job_id,))
    rows = cursor.fetchall()
    for r in rows:
        results[r[0]] = r[1]
    cursor.close()
    cnxn.close()
    return results


