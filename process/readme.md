## Sample Batch Processing Code

This is code that does some batch processing using las tools and saga_cmd.  It might be useful as sample code for getting started.

### Installation

This requires python 2.7.  If you have Anaconda installed, you can set up a 64-bit virtual environment by running an Anaconda command prompt, and executing these commands:

    ```
	set CONDA_FORCE_32BIT=
    conda create -n py27 python=2.7
    activate py27
    pip install numpy
	pip install boto
	pip install requests
	```
    To run and debug in pycharm, select py27 as the project interpreter.  The file config.py has paths to saga_cmd, lastools, and a local working directory that need to be set.

### Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D
