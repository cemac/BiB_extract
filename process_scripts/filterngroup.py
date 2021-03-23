import pandas as pd
import numpy as np
try:
    from pandarallel import pandarallel
    pandarallel.initialize(progress_bar=True)
    par = True
except ImportError:
    print('no pandarallel')
    par = False


__readfile__ = 'data.csv'


def todate(x):
    return pd.to_datetime(x['UNIXTIME'],unit='s').to_period('H')


df = pd.read_csv(__readfile__)

print('getting datetime')
if par:
    df['MINUTES'] = df.parallel_apply(todate,axis=1)
else:
    df['MINUTES'] = df.apply(todate,axis=1)

print('df loaded')

if par:
    dfg = df.groupby('MINUTES').parallel_apply(np.mean)
except:
    dfg = df.groupby('MINUTES').apply(np.mean)




print('fi')
