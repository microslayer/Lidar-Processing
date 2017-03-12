import os
import steps
import config as conf
import time as tm
import threading as th
import job_manager as jm
import las2grid as lg
from collections import defaultdict
import time as tm

# To install components in python34-64 when it is not the default python install, use this:
# c:\python34_64\python.exe c:\python34_64\Scripts\pip3.4.exe install numpy

# Running function so we can centralize timings and file cleanups
def run_function(f, input_file):
    print ("Starting:", f.__name__)
    output_file = f(input_file)
    # Deletes processed files to save space.
    try:
        os.remove(input_file)
    except Exception as e:
        print ("Could not delete LAS file.", e)
    return output_file

def process_tile(t, output_tiles):
    # Creata a local path for each file
    url = t["url"].replace("\n", "")
    file_name = str(t["id"]) + t["url"][-4:] # splitos.path.basename(url)
    cur_file = conf.work_path + file_name
    if os.path.isfile(cur_file.replace(".laz", "_max_z_float_3857.tif")):
        return
    steps.download_file(url, cur_file)
    jm.update_tile_status(t["id"], 1)  # File downloaded
    if cur_file.endswith(".laz"):
        cur_file = run_function(steps.convert_to_las, cur_file)
    grid_files = run_function(lg.generate_grids, cur_file)
    jm.update_tile_status(t["id"], 2)  # Grids created

    for k in grid_files.keys():
        cur_file = run_function(steps.export_tiff, grid_files[k])
        output_tiles[k].append(run_function(steps.add_srs_to_tiff, cur_file))
    jm.update_tile_status(t["id"], 3)  # Tiffs created

def create_layer(job_id, layer_name, identifier, file_list):
    mosaic = steps.mosaic_tiles(file_list, job_id, identifier)
    mosaic = steps.add_srs_to_tiff(mosaic)
    steps.create_output_tiles(mosaic, identifier + "/")
    jm.add_map_layer(job_id, layer_name, identifier + "/")

def main():
    # Get list of files to process from s3 bucket
    while (True):
        tm.sleep(conf.sleep_time_in_seconds) # Wait for 10 seconds before continuing, to let other tasks run.
        job_id = jm.start_available_job()
        if not job_id is None:
            jm.update_job_status(job_id, 2)  # Set status to processing
            output_tiles = defaultdict(list)
            overall_start_time = tm.time()
            tiles = jm.get_tiles_to_process(job_id)
            # Process each one
            for t in tiles:
                # For debugging:
                # output_tiles["max_z"].append(conf.work_path + str(t["id"]) + "_max_z_float_3857.tif")
                # output_tiles["range_z"].append(conf.work_path + str(t["id"]) + "_range_z_float_3857.tif")
                # output_tiles["mean_i"].append(conf.work_path + str(t["id"]) + "_mean_i_float_3857.tif")
                # continue
                start_time = tm.time()
                try:
                    process_tile(t, output_tiles)
                except Exception as ex:
                    print ("Exception processsing tile {0}".format(str(t)), ex)
                finally:
                    print ("***************************************************************")
                    print ("Time for: " + str(t) + ": " + str(round(tm.time() - start_time, 2)))
                    print ("***************************************************************")
            jm.update_job_status(job_id, 3)  # Set status to map generation
            create_layer(job_id, "Surface model", str(job_id) + "_dsm", output_tiles["max_z"])
            create_layer(job_id, "Height", str(job_id) + "_height", output_tiles["range_z"])
            create_layer(job_id, "Intensity", str(job_id) + "_intensity", output_tiles["mean_i"])
            jm.update_job_status(job_id, 4)  # Set status to done
    print ("All done!")
    print("Elapsed time:", tm.time() - overall_start_time)

if __name__ == "__main__":
    main()