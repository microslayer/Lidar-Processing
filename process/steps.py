import xmltodict
import requests
import subprocess as sb
import config as conf
import laspy as ls
import numpy as np
import math
import os
import boto
from boto.s3.key import Key

def get_urls_to_process():
    # Requires pip install requests
    # Also requires xmltodict.py in current directory
    # TODO: replace with web service call that reserves files for local processing
    results = []
    s3url = conf.s3_url
    r = requests.get(s3url)
    r.encoding = 'utf-8'
    xml_str = r.text
    xml_dict = xmltodict.parse(xml_str)
    for f in xml_dict["ListBucketResult"]["Contents"]:
        results.append(s3url + "/" + f["Key"])
    return results

def download_file(url, file_name):
    req = requests.get(url, stream=True)
    with open(file_name, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

def convert_to_las(input_file):
    cmd = conf.las_tools_dir + 'las2las -i "{0}" -odir "{1}" -olas'.format(input_file, conf.work_path)
    sb.call(cmd, shell=False)
    return input_file.replace(".laz", ".las")

def reproject_to_text(input_file):
    """"
    Be sure laspy folder is in the current directory

    Execute these commands at the command line:
    set CONDA_FORCE_32BIT=
    conda create -n py27 python=2.7
    activate py27
    pip install numpy

    In pycharm, selecct this virtual environment as the project interpreter
    """
    f = ls.file.File(input_file, mode="rw")
    x = (f.X * f.header.scale[0]) + f.header.offset[0]
    y = (f.Y * f.header.scale[1]) + f.header.offset[1]

    # Projection from https://gist.github.com/springmeyer/871897, vectorized with numpy
    n = len(f.points)
    x = (x * 20037508.34 / 180.0)
    y = (np.log(np.tan((90.0 + y) * math.pi / 360.0)) / (math.pi / 180.0)* 20037508.34 / 180.0)
    z = (f.Z * f.header.scale[2])
    out_file = input_file.replace(".las", "_3857.txt")
    counter = 0
    with open(out_file, "w") as txt_file:
        for i in range(x.shape[0]):
            counter += 1
            line = " ".join([str(num) for num in [x[i], y[i], z[i]]]) + "\n"
            txt_file.write(line)
            if (counter % 100000) == 0:
                print ("Processed {0} of {1} points ({2}%)".format(counter, n,
                    round(100 * float(counter) / n), 0))
    f.close()
    return out_file

def create_point_cloud(input_file):
    output_file = input_file.replace(".txt", "")
    cmd = conf.saga_cmd_dir + "saga_cmd io_shapes 16 -POINTS={1} -FILE={0} -XFIELD=1 -YFIELD=2 -ZFIELD=3 -SKIP_HEADER=0 -FIELDSEP=1".format(input_file, output_file)
    sb.call(cmd, shell=False)
    return output_file + ".spc"

def create_grid(input_file):
    output_file = input_file.replace(".spc", "")
    cmd = "saga_cmd pointcloud_tools 4 -POINTS={0} -OUTPUT=0 -GRID={1} -AGGREGATION=4 -CELLSIZE=1.000000".format(input_file, output_file)
    sb.call(cmd, shell=False)
    return output_file + ".sdat"

def fill_grid_gaps(input_file):
    output_file = input_file.replace(".sdat", "_closed.sdat")
    cmd = "saga_cmd grid_tools 7 -INPUT={0} -RESULT={1} -THRESHOLD=0.100000".format(input_file, output_file)
    sb.call(cmd, shell=False)
    return output_file

def export_tiff(input_file):
    output_file = input_file.replace(".sdat", ".tif")
    # Exports as rendered 8-bit raster
    cmd = "saga_cmd io_gdal 1 -GRIDS={0} -FILE={1} -FORMAT=7 -TYPE=1 -SET_NODATA=0 -NODATA=3.000000 -OPTIONS=".format(input_file, output_file)
    # Exports as floating point raster
    # cmd = conf.saga_cmd_dir + "saga_cmd io_gdal 2 -GRIDS={0} -FILE={1} -OPTIONS=".format(input_file, output_file)
    sb.call(cmd, shell=False)
    return output_file

def add_srs_to_tiff(input_file):
    output_file = input_file.replace(".tif", "_3857.tif")
    cmd = conf.gdal_dir + "gdal_translate.exe -a_srs EPSG:3857 {0} {1}".format(input_file, output_file)
    sb.call(cmd, shell=False)
    return output_file

def upload_to_s3(source_file):
    """
    This requirse Amazon boto module - pip install boto
    """
    bucket = conf.output_bucket
    aws_access_key_id = conf.s3_access_key
    aws_secret_access_key = conf.secret_access_key
    conn = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
    bucket = conn.get_bucket(bucket, validate=True)
    dest_file = os.path.basename(source_file).replace(".txt", "")
    k = Key(bucket)
    k.key = dest_file
    target_size = os.path.getsize(source_file)
    uploaded_size = k.set_contents_from_filename(source_file)
    if target_size == uploaded_size:
        return True
    return False