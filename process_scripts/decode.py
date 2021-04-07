
# make sure the following are imported
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

import pandas as pd
import numpy as np
import time,os,sys,pickle

try:
    from pandarallel import pandarallel
    pandarallel.initialize(progress_bar=True)
    par = True
except ImportError:
    print('no pandarallel')
    print('WARN :: Not using the multiple cores on your computer significally increases computation time for location and date decoding.')
    par = False


import sys
sys.path.insert(0, "../")
from config import __KEY__


#########      Private device only    ##########
def read_private (filename):
    with open(filename, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key



'''
Get datetime for df
'''
def todate(x):
    return pd.to_datetime(x['UNIXTIME'],unit='s')
def par_date(df):
    global par
    if par:
        df.index = df.parallel_apply(todate,axis=1)
    else:
        df.index = df.apply(todate,axis=1)
    return df



def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)





'''
Function globals
'''

try:
    private_key = read_private(__KEY__)
    algorithm = padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
except:None

'''
Location functions
'''

def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - degrees)/0.6
    return degrees + mm_mmmm

def parse(buff):
    # __KEY__ = '/Users/wolfiex/bbkey/decrypt.pem'
    # private_key = read_private(__KEY__)
    # algorithm = padding.OAEP(
    #         mgf=padding.MGF1(algorithm=hashes.SHA256()),
    #         algorithm=hashes.SHA256(),
    #         label=None
    #     )
    try: loc = private_key.decrypt( buff, algorithm ).decode('utf-8')
    except Exception as e:
        print(e)
        return [None,None,None]

    if loc == '__': return [np.nan,np.nan,np.nan]
    else:
        loc = loc.split('_')
        for i in [0,1]: loc[i] = convert_to_degrees(float(loc[i]))
        loc[2] = float(loc[2])
        return loc



'''
Get the BINS
'''
def par_bins(df):
    global par
    start = time.time()

    if par:
        df.BINS = df.BINS.parallel_map(pickle.loads)
    else:
        df.BINS = df.BINS.map(pickle.loads)

    end = time.time()
    total = (end-start)/60


    times = 'Bins extraction took %.2f minutes'%(total)

    return df.set_index('index'),times


'''
Get the location
'''

def par_loc(df,real=True):
    global par
    start = time.time()

    '''
    get values
    '''
    if par:
        ret = df.LOC.parallel_map(parse)
    else:
        ret = df.LOC.map(parse)


    mid = time.time()
    print('\n merging df')

    '''
    merge the two together
    '''
    df = pd.concat( [df.drop('LOC',axis=1), pd.DataFrame(data = ret.tolist(),columns='LAT LON ALT'.split())], axis = 1  )

    '''
    get only the real results
    '''
    if real: df = df[np.isnan(df.LAT)==False]

    end = time.time()
    total = (end-start)/60
    parsetime = (end-mid)/60


    times = 'This took %.2f minutes, of which decryption was %.2f minutes'%(total,parsetime)

    return df.set_index('index'),times
