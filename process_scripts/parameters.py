import pandas as pd


params = {

'start_date': None,
'end_date': None,
'start_date_str':None,
'end_date_str':None,
'sliders':[],
# 'get_loc': False,
# 'get_bins': False,
# 'get_all': False,
# 'anon': False,
# 'group': False, 
'columns':['UNIXTIME']

}



def startup(conn,info):

    dblength = conn.execute("SELECT COUNT(UNIXTIME) from MEASUREMENTS").fetchone()[0]
    info('Database length:'+ str(dblength))

    # "PRAGMA table_info(MEASUREMENTS)"

    info('Column Names\n')
    cols = pd.read_sql_query("PRAGMA table_info(MEASUREMENTS)", conn).name.values
    info(cols)


    info('Calculating time range...')
    dbrange = pd.to_datetime([conn.execute("SELECT %s(UNIXTIME) from MEASUREMENTS"%i).fetchone()[0] for i in ['MIN','MAX']],unit='s')
    info('Min-Max Datetime:' + str(dbrange.astype(str).values))


    background = pd.DataFrame([['Start Date',dbrange[0]],['End Date',dbrange[1]],['No Items',dblength],['columns',' | '.join(cols)]],columns = ['Name','Value'])


    return dblength, cols, dbrange, background