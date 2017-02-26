import xmltodict
import requests
import subprocess as sb
import config as conf
import las2grid as lg

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

def export_text(arr, out_file):
    counter = 0

    # Generate max z file for DSM
    with open(out_file, "w") as txt_file:
        for a in arr.iterrows():
            line = " ".join([str(a[0][0]), str(a[0][1]), str(a[1].z)]) + "\n"
            txt_file.write(line)
            counter += 1
            if (counter % 100000) == 0:
                print ("Processed {0} points".format(counter))

    return


def generate_grids(input_file):
    out_files = lg.generate_grids(input_file)
    return out_files

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
    # output_file = input_file.replace(".sdat", ".tif")
    # Exports as rendered 8-bit raster
    #Q cmd = "saga_cmd io_gdal 1 -GRIDS={0} -FILE={1} -FORMAT=7 -TYPE=1 -SET_NODATA=0 -NODATA=3.000000 -OPTIONS=".format(input_file, output_file)
    # sb.call(cmd, shell=False)
    # Exports as floating point raster
    output_file = input_file.replace(".sdat", "_float.tif")
    cmd = conf.saga_cmd_dir + "saga_cmd io_gdal 2 -GRIDS={0} -FILE={1} -OPTIONS=".format(input_file, output_file)
    sb.call(cmd, shell=False)
    return output_file

def add_srs_to_tiff(input_file):
    output_file = input_file.replace(".tif", "_3857.tif")
    cmd = conf.gdal_dir + "gdal_translate.exe -a_srs EPSG:3857 {0} {1}".format(input_file, output_file)
    sb.call(cmd, shell=False)
    return output_file
