# ##############################################################################
# Code to use laspy to load data into pandas and numpy arrays, to get grid values
# more efficiently, without any point-by-point iteration.
# ##############################################################################

import numpy as np
import math
import laspy as ls
import pandas as pd
import subprocess as sb
import config as conf
import os

""""
Be sure laspy folder is in the current directory

Execute these commands at the command line:
set CONDA_FORCE_32BIT=
conda create -n py27 python=2.7
activate py27
pip install numpy
pip install pandas

In pycharm, selecct the py27 virtual environment as the project interpreter
When running from the command-line, type activate ph27 before running
"""

def write_bin_file(file_name, arr, bit_depth, x_min, y_min, no_data_value):

    # bit depths:
    # 0 = unsigned byte
    # 2 = unsigned 2-byte word
    # 3 = signed integer
    # 6 = 32-bit float

    # Save numpy file as raw binary with the relevant bit depth.
    dt = np.float32
    if bit_depth == 3:
        dt = np.int32
    np.save(file_name, arr.astype(dt))

    # Numpy will add .npy by defult - remove to get the base file name, and let saga import the data
    output_file = file_name.replace(".npy", "")
    cmd = "saga_cmd io_grid 4 -GRID={0} -FILE_DATA={1} -NX={2} -NY={3} -DXY=1.000000 -XMIN={4} -YMIN={5} -UNIT= " \
          "-ZFACTOR=1.000000 -NODATA={6} -DATA_OFFSET=0 -LINE_OFFSET=0 -LINE_ENDSET=0 -DATA_TYPE={7} " \
          "-BYTEORDER_BIG=0 -TOPDOWN=0"
    cmd = cmd.format(output_file, file_name, arr.shape[1], arr.shape[0], x_min,
                     y_min, no_data_value, bit_depth)
    sb.call(cmd, shell=False)

    # Delete files to save space.
    try:
        os.remove(file_name)
    except Exception as e:
        print ("Could not delete LAS file.", e)
    return output_file + ".sdat"


def generate_grids(input_file):
    no_data_value = -1
    output_files = {}

    # Read in las file with laspy
    f = ls.file.File(input_file, mode="rw")
    x = (f.X * f.header.scale[0]) + f.header.offset[0]
    y = (f.Y * f.header.scale[1]) + f.header.offset[1]

    # Projection from https://gist.github.com/springmeyer/871897, vectorized with numpy
    x = (x * 20037508.34 / 180.0)
    y = (np.log(np.tan((90.0 + y) * math.pi / 360.0)) / (math.pi / 180.0) * 20037508.34 / 180.0)
    z = (f.Z * f.header.scale[2])

    # Create int array for indexing grid x, y
    x_int = np.floor(x + 0.5).astype(np.int32)
    y_int = np.floor(y + 0.5).astype(np.int32)

    # Convert to range starting with zero
    x_int = x_int - x_int.min()
    y_int = y_int - y_int.min()

    # Create xyz numpy arrays from points array, where z is elevation, classification, intensity,
    # return number, and number of returns.
    xyz = np.vstack([x_int, y_int, z]).transpose().astype(np.int32)
    xyc = np.vstack([x_int, y_int, f.classification]).transpose().astype(np.int32)
    xyi = np.vstack([x_int, y_int, f.intensity]).transpose().astype(np.int32)
    # Todo - change minz to last returns only; maxz to be first returns only.

    # Create a pandas dataframe to make it easier to slice and dice the arrays. Max, min, range z.
    df = pd.DataFrame(xyz)
    df.columns = ['x', 'y', 'z']
    max_z = df.groupby(['x', 'y'], sort=False).max()
    min_z = df.groupby(['x', 'y'], sort=False).min()
    range_z = max_z - min_z

    # Create numpy array for gridded ouitput, and set it to no_data_value. Existing are x/y combinations
    # where points exists.
    arr = np.zeros((y_int.max()+1, x_int.max()+1))
    existing_x = [rt[0] for rt in max_z.index]
    existing_y = [rt[1] for rt in max_z.index]

    # Output max z
    arr[:, :] = no_data_value
    arr[existing_y, existing_x] = max_z.z.values
    new_file = write_bin_file(input_file.replace(".las", "_max_z.npy"), arr, 6,  x.min(), y.min(), no_data_value)
    output_files["max_z"] = new_file

    # Output min z
    arr[:, :] = no_data_value
    arr[existing_y, existing_x] = min_z.z.values
    new_file = write_bin_file(input_file.replace(".las", "_min_z.npy"), arr, 6,  x.min(), y.min(), no_data_value)
    output_files["min_z"] = new_file

    # Output range z
    arr[:,:] = no_data_value
    arr[existing_y, existing_x] = range_z.z.values
    new_file = write_bin_file(input_file.replace(".las", "_range_z.npy"), arr, 6,  x.min(), y.min(), no_data_value)
    output_files["range_z"] = new_file

    # Clean up - seems to help reduce memory usage a bit
    max_z = None
    min_z = None
    range_z = None
    df = None

    # Classification
    df = pd.DataFrame(xyc)
    df.columns = ['x', 'y', 'z']
    max_c = df.groupby(['x', 'y'], sort=False).max()

    # Output classification
    arr[:,:] = no_data_value
    arr[existing_y, existing_x] = max_c.z.values
    new_file = write_bin_file(input_file.replace(".las", "_class.npy"), arr, 6,  x.min(), y.min(), no_data_value)
    output_files["max_c"] = new_file

    # Clean up
    max_c = None
    df = None

    # Intensity
    df = pd.DataFrame(xyi)
    df.columns = ['x', 'y', 'z']
    mean_i = df.groupby(['x', 'y'], sort=False).mean()

    # Output intensity
    arr[:,:] = no_data_value
    arr[existing_y, existing_x] = mean_i.z.values
    new_file = write_bin_file(input_file.replace(".las", "_intensity.npy"), arr, 6,  x.min(), y.min(), no_data_value)
    output_files["mean_i"] = new_file

    # Clean up
    max_i = None

    return output_files

# For debugging - you can display gridded numpy arrays in matplotlib:
# pip install matplotlib
# import matplotlib.pyplot as plt
# plt.imshow(arr)

if __name__ == "__main__":
    # Single test file:
    output_files = generate_grids("C:/Projects/lidar-data/test_file/20150429_QL1_18TXM690689_SW_1.las")