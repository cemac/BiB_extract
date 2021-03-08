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
'columns':['UNIXTIME'],
'precompute':False,

}



def startup(conn,info):

    dblength = conn.execute("SELECT COUNT(UNIXTIME) from MEASUREMENTS").fetchone()[0]
    info('Database length:'+ str(dblength))

    # "PRAGMA table_info(MEASUREMENTS)"

    info('Column Names\n')
    cols = pd.read_sql_query("PRAGMA table_info(MEASUREMENTS)", conn).name.values
    info(cols)


    info('Calculating time range...')
    dates = [conn.execute("SELECT %s(UNIXTIME) from MEASUREMENTS"%i).fetchone()[0] for i in ['MIN','MAX']]
    dbrange = pd.to_datetime(dates,unit='s')
    info('Min-Max Datetime:' + str(dbrange.astype(str).values))


    background = pd.DataFrame([['Start Date',dbrange[0]],['End Date',dbrange[1]],['No Items',dblength],['columns',' | '.join(cols)]],columns = ['Name','Value'])


    start_date = dbrange[0]
    end_date = dbrange[1]
    
    # if start_date== end_date:
    #     info('START === END : adding a day')
    #     from datetime import timedelta
    #     end_date +=  timedelta(days=1)
    # not needed as ut uses actual datetimes
    
    params['start_date_str'] = str(start_date)
    params['end_date_str'] = str(end_date)

    #"%Y-%m-%dT%H:%M:%S"
    params['start_date'] = int(dates[0])
    params['end_date']   = int(dates[1])
        
    # params['sliders'] = []
    selected = ["UNIXTIME"]
    pm = list(filter(lambda x: 'PM' in x, cols))
    selected.extend(pm)
    params['columns'] = selected

    return dblength, cols, dbrange, background,params