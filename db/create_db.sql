CREATE DATABASE lidar_maps
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

CREATE TABLE public.batch_tile
(
    batch_tile_id integer NOT NULL DEFAULT nextval('batch_tile_batch_tile_id_seq'::regclass),
    job_id character varying(50) COLLATE pg_catalog."default" NOT NULL,
    tile_url character varying(500) COLLATE pg_catalog."default" NOT NULL,
    status smallint NOT NULL,
    CONSTRAINT batch_tile_pkey PRIMARY KEY (batch_tile_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;