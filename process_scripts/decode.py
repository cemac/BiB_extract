
# make sure the following are imported
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

import pandas as pd
import numpy as np
import time,os,sys

from pandarallel import pandarallel
# pandarallel.initialize()
pandarallel.initialize(progress_bar=True)


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
    df.index = df.parallel_apply(todate,axis=1)
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


private_key = read_private(__KEY__)
algorithm = padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )

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
Get the location 
'''
def par_loc(df,real=True):
    

    start = time.time()


    ''' 
    get values
    '''
    
    
    ret = df.LOC.parallel_map(parse)

    
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

    return df,times




