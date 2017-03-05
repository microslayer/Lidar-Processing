import os
import steps
import config as conf
import time as tm

# Running function so we can centralize timings and file cleanups
def run_function(f, input_file):
    print ("Starting:", str(f))
    output_file = f(input_file)
    # Deletes processed files to save space.
    try:
        os.remove(input_file)
    except Exception as e:
        print ("Could not delete LAS file.", e)
    return output_file

def main():
    # Get list of files to process from s3 bucket
    urls_to_process = steps.get_urls_to_process()
    overall_start_time = tm.time()
    # Process each one
    for url in urls_to_process:
        start_time = tm.time()
        try:
            # Creata a local path for each file
            file_name = os.path.basename(url)
            cur_file = conf.work_path + file_name
            # TODO: move processed-file tracking into db/services:
            if os.path.isfile(cur_file.replace(".laz", "_max_z_float_3857.tif")):
                continue
            # First download the file to a local directory
            steps.download_file(url, cur_file)
            # Then run each step in sequence
            if cur_file.endswith(".laz"):
                cur_file = run_function(steps.convert_to_las, cur_file)
            grid_files = run_function(steps.generate_grids, cur_file)
            for f in grid_files:
                # cur_file = run_function(steps.create_point_cloud, f)
                # cur_file = run_function(steps.create_grid, cur_file)
                # cur_file = run_function(steps.fill_grid_gaps, f)
                cur_file = run_function(steps.export_tiff, f)
                run_function(steps.add_srs_to_tiff, cur_file)
        except Exception as ex:
            print ("Exception processsing tile {0}".format(cur_file), ex)
        finally:
            print ("***************************************************************")
            print ("Time for: " + url + ": " + str(round(tm.time() - start_time, 2)))
            print ("***************************************************************")

    print ("All done!")
    print("Elapsed time:", tm.time() - overall_start_time)

if __name__ == "__main__":
    main()