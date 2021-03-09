# BiB_extract
An extraction app for the encrypted sensor databases. 

# Quickstart
- `conda activate bib`
- setup `config.py `
- `python app.py`
- navigate to `http://127.0.0.1:8050/` in a web browser - chrome works well

# Command Line interface
For information on the command line interface (non-gui), type in `python bib_cli.py --help` or visit the documentation at: 

https://daniel-ellis.medium.com/using-the-borninbradford-sql-database-extract-command-line-interface-f6db6a910c11



#### Port in use error 
If you get a message that the port is already in use, that means a previous version of the code has not been terminated cleanly. Use (with caution!)`pkill -9 python` for linux or windows task manager to close all python instances before trying again. 



## Install 
1. Start by installing conda on the windows subsystem as shown in 
http://mmb.irbbarcelona.org/webdev/slim/molywood/public/tutorials/windows_sub

2. Open command line/terminal 
3. Create conda environment: `conda env create -f bibview.yml`


## Configuration `config.py`

### Setting up the decode key (only needed if you are decoding the locations)
We are interested in the file named `decode.pem`. 
** DO NOT PLACE THIS IN THE SAME LOCATION AS THE DATA OR THIS LIBRARY ** 

In we can set this as the `__KEY__` variable in config.py. 


## database locations
The `__DBLOC__` in `config.py` sets the location of the database we are interested in. This can either be the merged database, or a local copy from an individual sensor. 

## save location
If you plan on saving any extracted data, you will need to set the directory in which you want the output CSV to be saved. 









## ToDo
- [ ] command line arguments 
- [ ] module command for use on ARC
- [ ] groupby hour
- [ ] negatives on lon (sensor of decode issue?)
- [ ] awaiting new dash version to fix superclustering 
- [ ] bin merging
  
## Note: 
On Windows, Pandarallel will works only if the Python session (python, ipython, jupyter notebook, jupyter lab, ...) is executed from Windows Subsystem for Linux (WSL).