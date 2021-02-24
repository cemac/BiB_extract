'''
The main app used to access the merged sensor database 

Author: D. Ellis, d.ellis@-nospam-@leeds.ac.uk @CEMAC

'''



''' 
Constants
'''
__DBLOC__ = 'merged.db'
## change database location as required. This presumes that it is located within the current directory. 
__SAVELOC__ = './'


'''
Imports
'''
import dash,sqlite3,sys
import dash_daq as daq
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime
import plotly.express as px
from process_scripts import log_manager
from process_scripts.components import *
from process_scripts.mdtext import *
from process_scripts.readsql import *
from process_scripts.parameters import params, startup
'''
Additional Setup
'''
if sys.version[0]!= '3':
	sys.exit('You are not using python 3 - ** sadface **')
    
log = log_manager.getlog(__name__)
info = log.info

info('Loading Database')
conn = sqlite3.connect(__DBLOC__,check_same_thread=False)# need this to work in flask

# tables = conn.execute('SELECT * from sqlite_master').fetchall()
# info('tables ' +str(tables))




''' 
Main Application
'''
external_stylesheets = [dbc.themes.COSMO]#'https://codepen.io/anon/pen/mardKv.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = None


'''
Layout

https://bootswatch.com/cosmo/
'''
dblength, cols, dbrange, background = startup(conn,info)

'''
Left column Row 1
'''
bginfo = dbc.Row(
            style = center,
            align="center",
            children = [
                header,# introduction

                
                
                
                
            ],)

leftcol = dbc.Col(
            style = center,
            align="center",
            children = [
                timein,# md time desc 
                daterange(dbrange,app), # date selector
                br,br,
                postparse(cols),
                br,
                multiselect(cols)
            ],)

rightcol= dbc.Col(
            style = center,
            align="center",
            children = [
            br,br,
            md(instructions,id='buttoninstructions'),
            button('get_size','Precompute Fetch'),
            br,
            html.Div(children=[],id='precomputedata'),
            button('get_data','Extract',clr='success',disabled=True),
            button('get_csv','Download CSV',clr='secondary',disabled=True),
            
            ],)


'''
TABS
'''
tab = dbc.Card([
    dbc.CardBody(
    [
        dbc.Row([   md('## Instructions '),
        br,br, table(background,'info_table',{'width':'80%','margin':'auto'})]),
        br,
    ]),
    dbc.CardBody(
    [    
    br,
        dbc.Row([leftcol,rightcol]),
    ] # selection row
    )],
    className="mt-3",
)


#### TABLE
tab_table = dbc.Card(
    dbc.CardBody(   
    dcc.Loading(id = 'table_spin',
    children=['No database Loaded'])),
    className="mt-3",
)


# LINEPLOT
tab_lineplot = dbc.Card(
    dbc.CardBody(    [      
    br,
    dcc.Loading(
        id="scatter_spin",
        type="default",
        children=[]
    )
    ]
    ),
    className="mt-3",
)



    
tab_leaflet = dbc.Card(
    dbc.CardBody(       
        br
    ),
    className="mt-3",
)
    

tabs = dbc.Tabs(
    [
        dbc.Tab(tab, label="Filter Parameters",tab_id='base'),
        dbc.Tab(tab_table, label="View Table",tab_id ='table_tab'),
        dbc.Tab(tab_lineplot, label="View Scatter",tab_id='scatter_tab'
        ),
        dbc.Tab(tab_leaflet, label="View Map",disabled=True),

    ],
    active_tab='base',
    id='tabs'
)


'''
APP LAYOUT
'''
app.layout = html.Div(
style=center,
 children = [

        bginfo,br,# first row
        
        tabs,
        
])


'''
OPTIONS
'''

ho = lambda x: Output('h_'+x,'n_clicks')
so = Input('date', 'start_date')
eo = Input('date', 'end_date')
po = Input('post_process', 'value')
io = Input('itemselect', 'value')

@app.callback([Output("get_csv",'style'),Output("get_data",'style'),Output("precomputedata",'children')], [so,eo,po,io])
def update_range(start_date, end_date,slide,cols): 
    global params,df
    
    print(start_date)
    del df
    df = None
    
    start_date = start_date.split('T')[0]
    end_date = end_date.split('T')[0]
    
    
    params['start_date_str'] = start_date
    params['end_date_str'] = end_date

    #"%Y-%m-%dT%H:%M:%S"
    params['start_date'] = int((datetime.strptime(start_date, "%Y-%m-%d")-datetime(1970,1,1)).total_seconds())
    params['end_date']   = int((datetime.strptime(end_date, "%Y-%m-%d")-datetime(1970,1,1)).total_seconds())
        
    params['sliders'] = slide    
    params['columns'] = cols
        
    print(params['start_date'],params['end_date'])
    return {'visibility':'hidden'},{'visibility':'hidden'},[]
    







'''
Precompute
'''
@app.callback([Output("get_csv",'style'),Output("get_data",'style'),Output("precomputedata",'children'),Output("get_size_spinner", "children")], Input("get_size", "n_clicks"))
def input_triggers_spinner(value):
    global params,conn
    
    if params['start_date']== None: 
        return {'visibility':'hidden'},{'visibility':'hidden'},[],None ## we are still loading
    
    
    print(params)

        
        
    print('diff')
    sqlquery = makesql(params,count=True)
    #"SELECT COUNT() from MEASUREMENTS where UNIXTIME between %(start_date)d and %(end_date)d"%params
    print(sqlquery)
    
    scount = conn.execute(sqlquery).fetchone()[0]
    
    print(scount)
    
    
    sdata = {'SQL Query':makesql(params), '# Rows': scount, 'Size Estimate':'Manual * rownumber'}
    
    series = pd.DataFrame(data=zip(sdata,sdata.values()), columns=['Description','Value'])
    
    time.sleep(1)
    return {'visibility':'hidden'},{'visibility':'visible'},table(series,tid = 'precompt'),None





'''
Extract
'''
@app.callback([Output("get_csv",'style'),Output("get_data_spinner", "children")], Input("get_data", "n_clicks"))
def input_triggers_spinner2(value):
    global params,conn,df

    if params['start_date']== None: return {'visibility':'visible'},None ## we are still loading

    sqlquery = makesql(params)
    
    df = pd.read_sql_query(sqlquery, conn)

    print(df)

    return {'visibility':'visible'},None

    
    



'''
save
'''
@app.callback(Output("get_csv_spinner", "children"), Input("get_csv", "n_clicks"))
def input_triggers_spinner3(value):
    global params, df
    
    if type(df)== type(None):return None
    
    loc = __SAVELOC__+'data.csv'
    df.to_csv(loc)
    return ['Saved']






''' 
Table
'''
@app.callback([Output("table_spin", "children"),Output("scatter_spin", "children")], Input("tabs", "active_tab"))
def tabulate(activetabs):
    global df
    
    
    if type(df) != type(None):
        if activetabs == 'table_tab': 

            return ['Showing the first 1000 values of the dataframe',br,table(df.iloc[:1000],'tab_table',{'width':'80%','margin':'auto'})],None


        elif activetabs == 'scatter_tab': 
            
            
            fig = px.scatter(df.iloc[:2000], x="PM1", y="PM10",
                             size="PM1", color="SERIAL", hover_name="SERIAL",
                             log_x=False, size_max=6)

            g = dcc.Graph(
                    id='plot',
                    figure=fig
                )
                
            return None,['Plotting first 2000 points', br,br,g]

        else:
            return None,None

    else:
        return None,None


'''
start Application
'''
if __name__ == '__main__':
    app.run_server(debug=True)