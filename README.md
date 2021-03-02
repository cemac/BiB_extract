# BiB_extract
An extraction app for the encrypted sensor databases. 


## Install 
1. Install anaconda python from continum.io
2. Open command line/terminal 
3. Create conda environment: 


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

## Note: 
On Windows, Pandarallel will works only if the Python session (python, ipython, jupyter notebook, jupyter lab, ...) is executed from Windows Subsystem for Linux (WSL).