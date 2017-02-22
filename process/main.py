import os
import steps
import config as conf
import time as tm

# Running function so we can centralize timings and file cleanups
def run_function(f, input_file):
    start_time = tm.time()
    print ("Starting:", str(f))
    output_file = f(input_file)
    # Deletes processed files to save space
    os.remove(input_file)
    print ("Elapsed:", round(tm.time() - start_time, 2))
    return output_file

def main():
    # Get list of files to process from s3 bucket
    urls_to_process = steps.get_urls_to_process()
    start_time = tm.time()
    print ("Start time: ", start_time)
    # Process each one
    output_files = []
    for url in urls_to_process:
        try:
            # Creata a local path for each file
            file_name = os.path.basename(url)
            cur_file = conf.work_path + file_name

            # First download the file to a local directory
            steps.download_file(url, cur_file)

            # Then run each step in sequence
            cur_file = run_function(steps.convert_to_las, cur_file)
            cur_file = run_function(steps.reproject_to_text, cur_file)
            cur_file = run_function(steps.create_point_cloud, cur_file)
            cur_file = run_function(steps.create_grid, cur_file)
            cur_file = run_function(steps.fill_grid_gaps, cur_file)
            cur_file = run_function(steps.export_tiff, cur_file)
            cur_file = run_function(steps.add_srs_to_tiff, cur_file)
            output_files.append(cur_file)
        except Exception as ex:
            print ("Exception processsing tile {0}".format(cur_file), ex)

    print ("All done!")
    print("Elapsed time:", tm.time() - start_time)
if __name__ == "__main__":
    main()