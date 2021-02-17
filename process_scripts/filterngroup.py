import pandas as pd
import numpy as np
from pandarallel import pandarallel
pandarallel.initialize()


__readfile__ = 'data.csv'


def todate(x):
    return pd.to_datetime(x['UNIXTIME'],unit='s').to_period('H')


df = pd.read_csv(__readfile__)

print('getting datetime')
df['MINUTES'] = df.parallel_apply(todate,axis=1)

print('df loaded')

dfg = df.groupby('MINUTES').parallel_apply(np.mean)




print('fi')