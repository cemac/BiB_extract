
# make sure the following are imported
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

import pandas as pd
import numpy as np
import sqlite3
import time,os,sys

from pandarallel import pandarallel
pandarallel.initialize()

'''
pip3 uninstall numpy #remove previously installed package
sudo apt install python3-numpy
'''

__KEY__ = "/users/wolfiex/decrypt.pem"
__DB__ = sys.argv[1]
__exportcsv__ = 'data_decrypt.csv'


#########      Private device only    ##########
def read_private (filename):
    with open(filename, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

#########      Private device only    ##########
read_data = []
private_key = read_private(__KEY__)

algorithm = padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None
)

def decrypt(encrypted):
    return private_key.decrypt( encrypted, algorithm )

def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    #position = "%.4f" %(position)
    return position

#@np.vectorize
def parse(buff):
    # print(len(buff), len(str(buff)))
    try:
        loc = decrypt(buff).decode('utf-8')
    except Exception as e:
        print(e)
        return [None,None,None]
        
    if loc == '__': return [np.nan,np.nan,np.nan]
    else:
        loc = loc.split('_')
        for i in [0,1]:
            loc[i] = convert_to_degrees(float(loc[i]))
        loc[2] = float(loc[2])
        return loc


#########      OPEN db       ##########
def todate(x):
    return pd.to_datetime(x['UNIXTIME'],unit='s')

# def todecode(x):
# 
#     [parse(i) for i in df.LOC.values]

def get_data(sqlstr = "SELECT * from MEASUREMENTS" ,real=False):
    # Read sqlite query results into a pandas DataFrame

    start = time.time()
    print('connecting to db')
    conn = sqlite3.connect(__DB__)
    df = pd.read_sql_query(sqlstr, conn)
    
    df = df.loc[:1000]

    print ('Extracting %d values using the SQL string: "%s"'%(len(df),sqlstr))

    df['DATE'] = df.parallel_apply(todate,axis=1)
    
    

    mid = time.time()
    print('getting locations')

    ret = df.LOC.parallel_map(parse)

    
    print('loc end')
    
    df = pd.concat( [df.drop('LOC',axis=1)  ,pd.DataFrame(data = ret.tolist(),columns='LAT LON ALT'.split())], axis =1  )

    if real: df = df[np.isnan(df.LAT)==False]

    conn.close()

    end = time.time()
    total = (end-start)/60
    parsetime = (end-mid)/60

    print('This took %.2f minutes, of which decryption was %.2f minutes'%(total,parsetime))

    return df




def get_csv(real = False):
    
    start = time.time()
    
    df = pd.read_csv(__DB__)
    df = df[df.SERIAL != 'SERIAL'] 

    df['DATE'] = pd.to_datetime(df['UNIXTIME'],unit='s')

    mid = time.time()

    ret = [parse(str(i)) for i in df.LOC.values]
    df = pd.concat( [df.drop('LOC',axis=1)  ,pd.DataFrame(data = ret,columns='LAT LON ALT'.split())], axis =1  )

    if real: df = df[np.isnan(df.LAT)==False]


    end = time.time()
    total = (end-start)/60
    parsetime = (end-mid)/60

    print('CSV took %.2f minutes, of which decryption was %.2f minutes'%(total,parsetime))

    return df[df.columns[1:]]
    



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





if __name__ == '__main__':
    if '.csv' in __DB__:
        df = get_csv()
    else:
        df = get_data(sqlstr = "SELECT * from MEASUREMENTS where TYPE = 2")
    
    df.to_csv(__exportcsv__)
    print (df.columns)
    print(df['TIME PM1 PM3 PM10 SP RC DATE LAT LON'.split()].tail(n=50))


    print(file_size(__exportcsv__))



