#!/usr/bin/python

import psycopg2
from init import config


def connect():
    #'connect to Postgres server'
    conn = None
    try:
        #read connection parameters'
        params = config()

        #connect to the PostgreSQl server'
        conn = psycopg2.connect(**params)

        #create a cursor'
        cur = conn.cursor()


        print('PostgresSQL database version:')
        cur.execute('Select version()')

        #show the server version'
        db_version = cur.fetchone()
        print (db_version)

    #'end server connection'
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def postRaster():
    """python
    raster2pgsql.py - s
    4269 - I - r *.tif - F
    myschema.demelevation - o
    elev.sql"""

    return None



if __name__ == '__main__':
    connect()
    postRaster()




