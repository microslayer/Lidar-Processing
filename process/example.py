# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Minimal stand-alone python script for running command-line utilities.  Doesn't require any special
# installed libraries - just plain vanilla python.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import subprocess as sb
import glob as gl
import config as cf

def process_file(input_file):
    output_file = input_file.replace(".tif", "_hillshade.tif")
    # Example GDAL command - could be SAGA, LAS Tools or other as needed:
    cmd = cf.gdal_dir + "gdaldem hillshade {0} {1}".format(input_file, output_file)
    sb.call(cmd, shell=False)
    return output_file

if __name__ == "__main__":
    # By iterating though files independently from main process function, we can
    # wire up the main function in a multi-threaded or multi-processing task runner
    # program later.
    for f_name in gl.glob('C:/Projects/lidar-data/*min_z.tif'):
        output_file = process_file(f_name)
        print ("Processed " + output_file)
