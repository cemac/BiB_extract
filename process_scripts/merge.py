'''
`sudo pip install awscli`
`aws config`
`aws s3 sync s3://bib-pilot-bucket .`
'''
import sqlite3,glob,os
import pandas as pd



files = glob.glob('upload*.db')
files.sort()

# save sensor file measurements for plotting
csvall=False
## create merge file
os.system('cp %s merge.db'%files[0])
#​
conn = sqlite3.connect('merge.db')
#​
#​
# df1 = pd.read_sql_query("SELECT * from MEASUREMENTS", conn)
#​
for f in files[1:]:
    print(f)
    try:
        conn.execute("attach './%s' as toMerge; "%files[2])
        conn.execute('BEGIN;')
        conn.execute('insert into MEASUREMENTS select * from toMerge.MEASUREMENTS; ')
        conn.execute('COMMIT;')
    except Exception as e:
        print('failed',f, e)
    
    conn.execute('detach toMerge;')
    conn.commit()
#​
print('merge.db created')
#​
if csvall:
    df = pd.read_sql_query("SELECT * from MEASUREMENTS where TYPE = 2", conn)
    df.to_csv('merged_all.csv')

