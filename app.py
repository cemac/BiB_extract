'''
The main app used to access the merged sensor database 

Author: D. Ellis, d.ellis@-nospam-@leeds.ac.uk @CEMAC

'''



''' 
Constants
'''
from config import __DBLOC__, __SAVELOC__, __KEY__


'''
Log Setup
'''
import sys
if sys.version[0]!= '3':
	sys.exit('You are not using python 3 - ** sadface **')

from process_scripts import log_manager
log = log_manager.getlog(__name__)
info = log.info

print(chr(27) + "[2J", '\n\n') ## clear console using escape characters
info('Importing Libraries')


'''
Imports
'''

import dash_leaflet as dl
            # import plotly.express as px
import dash_leaflet.express as dlx
            #https://github.com/thedirtyfew/dash-leaflet/issues/24
            
import dash,sqlite3,os,time
import dash_daq as daq
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

            
from process_scripts.components import *
from process_scripts.mdtext import *
from process_scripts.readsql import *
from process_scripts.parameters import  startup
from process_scripts.decode import *

if os.path.isfile(__KEY__): 
    haskey=True
else: 
    log.warning('LOC FILE: %s not found!'%__KEY__)
    haskey=False
    

info('Loading Database')

conn = sqlite3.connect(__DBLOC__,check_same_thread=False)# need this to work in flask

external_stylesheets = [dbc.themes.COSMO]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,prevent_initial_callbacks=True)
dblength, cols, dbrange, background, params = startup(conn,info)


''' 
Main Application
'''
#'https://codepen.io/anon/pen/mardKv.css']
df = None
changed = True
computing = False

'''
Layout https://bootswatch.com/cosmo/
'''


'''
Left column Row 1
'''
bginfo = dbc.Row(
            style = center,
            align="center",
            children = [
                banner,
                header,# introduction
                html.Div([],id='warn'),          
                #             html.Div(dl.Map(dl.TileLayer()),style={'width': '100vw', 'height': '90vh'}),
            ],)

leftcol = dbc.Col(
            style = center,
            align="center",
            children = [

                
                timein,# md time desc 
                daterange(dbrange,app), # date selector
                br,br,
                postparse(cols,haskey),
                br,
                multiselect(cols)
            ],)

rightcol= dbc.Col(
            style = center,
            align="center",
            children = [
            br,br,
            md(instructions,id='buttoninstructions'),
            br,
            button('get_size','Precompute Fetch'),
            br,
            html.Div(children=[],id='precomputedata'),
            button('get_data','Extract',clr='success',disabled=True),
            html.Div(children=[],id='postcomputedata'),
            button('get_csv','Download CSV',clr='secondary',disabled=True),
            html.Div(children=[],id='savedata'),
            ],)


'''
TABS
'''
tab_overview = dbc.Card([
    dbc.CardBody(
    [
        dbc.Row([introtab,
        br,br, table(background,'info_table',{'width':'80%','margin':'auto'})]),
        br,
    ]),
    ],
    className="mt-3",
)

tab = dbc.Card([
    dbc.CardBody(
    [  br,dbc.Row([leftcol,rightcol]),] # selection row
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
dcc.Loading(id = 'map_spin',
children=['No Map Loaded...'])),
className="mt-3",
)
    

tabs = dbc.Tabs(
    maketabs(tab_overview,tab,tab_table,tab_lineplot,tab_leaflet),
    active_tab='base',
    id='tabs'
)


'''
APP LAYOUT
'''
app.layout = html.Div(
style=center,
 children = [
 dcc.Location(id='url',refresh=False),
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

@app.callback([Output("get_csv",'style'),
Output("get_data",'style'),
Output("precomputedata",'children'),
Output("postcomputedata",'children'),
Output("warn",'children'),
Output("get_size",'disabled')
], [so,eo,po,io])
def update_range(start_date, end_date,slide,cols): 
    
    global params,df,changed,computing
    # print('change',params['precompute'])
    
    if not computing:
        warn = []
        if params['precompute']:
                
            del df
            df = None
            
            
            start_date = start_date.split('T')[0]
            end_date = end_date.split('T')[0]
            
            
            params['start_date_str'] = start_date
            params['end_date_str'] = end_date

            #"%Y-%m-%dT%H:%M:%S"
            params['start_date'] = int((datetime.strptime(start_date, "%Y-%m-%d")-datetime(1970,1,1)).total_seconds())
            # params['end_date']   = int((datetime.strptime(end_date, "%Y-%m-%d")-datetime(1970,1,1)).total_seconds())
                
            if params['start_date_str'] != params['end_date_str']:
                params['end_date']   = int((datetime.strptime(end_date, "%Y-%m-%d")-datetime(1970,1,1)).total_seconds())
            else:
                info('START === END : adding a day')
                params['end_date']   = int((datetime.strptime(end_date, "%Y-%m-%d")-datetime(1969,12,31)).total_seconds())
            
            
                    
            params['sliders'] = slide    
            params['columns'] = cols
                
            # print(params['start_date'],params['end_date'])
            info('inputs')
            print (params, start_date, end_date)
            changed=True
    else:
        warn = dbc.Alert("There is already a computation under way! Please do not change any options to prevent errors. If in doubt, restart app. ", color="danger")
        
    return {'visibility':'hidden'},{'visibility':'hidden'},[],[],warn,False
    







'''
Precompute
'''
@app.callback([Output("get_csv",'style'),
Output("get_data",'style'),
Output("precomputedata",'children'),
Output("get_size_spinner", "children"),
Output("postcomputedata",'children'),
Output("get_size",'disabled'),
Output("get_data",'disabled')
], Input("get_size", "n_clicks"))
def input_triggers_spinner(value):
    global params,conn,changed

    if (params['start_date']== None or not params['precompute']) or not changed: 
        return {'visibility':'hidden'},{'visibility':'hidden'},[],None ,None,False,False## we are still loading
    
    


    sqlquery = makesql(params,count=True)
    #"SELECT COUNT() from MEASUREMENTS where UNIXTIME between %(start_date)d and %(end_date)d"%params
    info(sqlquery)
    
    scount = conn.execute(sqlquery).fetchone()[0]
    
    
    
    print(scount)
    
    
    sdata = {'SQL Query':makesql(params), '# Rows': scount}#, 'Size Estimate':'Manual * rownumber'}
    
    series = pd.DataFrame(data=zip(sdata,sdata.values()), columns=['Description','Value'])
    
    
    # time.sleep(1)
    return {'visibility':'hidden'},{'visibility':'visible'},table(series,tid = 'precompt'),[],None,True,False






'''
Extract
'''
@app.callback([Output("get_csv",'style'),
Output("get_data_spinner", "children"),
Output("postcomputedata",'children'),
Output("itable_tab",'disabled'),
Output("iscatter_tab",'disabled'),
Output("imap_tab",'disabled'),
Output("get_data",'disabled')],
 Input("get_data", "n_clicks"))
def input_triggers_spinner2(value):
    global params,conn,df,changed,computing

    if computing:
        return {'visibility':'hidden'},[dbc.Spinner(color="Danger",size='sm')] ,None,True,True,True,True
    
    # print(computing,'computing')

    if params['start_date']== None or not params['precompute'] or not changed : return {'visibility':'hidden'},None ,br,True,True,True,False
    ## we are still loading
        
        
    log.debug(params)

    computing = True

    sqlquery = makesql(params)
    
    
    df = pd.read_sql_query(sqlquery, conn)
    info('extracted table')
    
    df = par_date(df)
    
    print(df,df.columns)
    
    loc=False
    group=False
    
    # if 'group' in params['sliders']:
    #     gc = 'PM1 PM3 PM2.5 PM10 T RH'.split()
    #     df = df[list(filter(lambda x:x in gc ,df.columns))]
    #     df['hour'] = df.index.to_period("H")
    #     info(df['hour'])
    #     df = df.groupby('hour').mean()
    #     group=True
    #     # info(df['hour'])

    if 'get_loc' in params['sliders']:
        info('decoding location data')
        df,ctime = par_loc(df.reset_index(),False) # false keeps bad locations
        if 'noloc' in params['sliders']:
            df.dropna(subset=['LON'],inplace = True)
        info(ctime)
        loc=True
    


    sdata = {'Shape':str(df.shape), 'Size in Memory': convert_bytes(sys.getsizeof(df))}
    series = pd.DataFrame(data=zip(sdata,sdata.values()), columns=['Description','Value'])

    
    # gc = 'PM1 PM3 PM2.5 PM10 T RH'.split()
    # cols = list(filter(lambda x:x in gc ,df.columns))
    # 
    
    # dropdown = dbc.DropdownMenu(
    # label="Select Plot Variable",id='pltdrop',
    # children=[dbc.DropdownMenuItem(i, href = '#'+i) for i in cols],
    # )


    changed = False
    computing = False
    time.sleep(.5)

    return {'visibility':'visible'},None, [ br, md('''
    
    ## Table, Grouped Scatter and GeoLocation tabs tab_overview
    If you want to explore the dataset you may need to scroll up.
    
    '''), br, table(series,tid = 'postcompt'),],False,False, not loc, True





# 
# 
# @app.callback([Output("pltdrop", "active")], [Input('url','pathname')])
# def hash(args):
# 
#         print(args)
# 
#         return [args]
# 



'''
save
'''
@app.callback(Output("get_csv_spinner", "children"), Input("get_csv", "n_clicks"))
def input_triggers_spinner3(value):
    global params, df
    
    if type(df)== type(None):return None
    
    loc = __SAVELOC__+'data.csv'
    df.to_csv(loc)
    return ['Saved '+ file_size(loc)]






''' 
TAB VIEW
'''
@app.callback([Output("table_spin", "children"),
Output("scatter_spin", "children"),
Output("map_spin", "children")],
 [Input("tabs", "active_tab"),Input('url','hash')])
def tabulate(activetabs,hashkey):
    global df,params
    # 
    # print
    # (activetabs,hashkey)
    
    if activetabs == 'filter':
        info('enabling filter options')
        params['precompute']= True
        return None,None,None
    
    
    if type(df) != type(None):
        
        # '''
        # table 
        # '''
        
        if activetabs == 'table_tab': 

            message = md('''
            # Table Sample
            Showing a *random* sample of *500* values from the selected dataframe
            ''')
            
            newdf = df.sample(500).reset_index()
            try: newdf.drop(['UNIXTIME'],inplace=True)
            except: None
            
            print(newdf)
            return [message,br,table(newdf,'tab_table',{'width':'80%','margin':'auto'})],None,None


        # '''
        # scatter_tab
        # '''
        elif activetabs == 'scatter_tab': 
        
            gc = 'PM1 PM3 PM2.5 PM10 UNIXTIME'.split()
            cols = list(filter(lambda x:x in gc ,df.columns))
            
            dfp = df[cols] 
            dfp['hour'] = df.index.hour + (df.index.minute/15)//4
            
            
            dfp = dfp.groupby('hour').mean().reset_index()

            
            print(dfp)
            
            sizes = {'PM1':2,'PM2.5':3, 'PM3':3, 'PM10':10}
            alpha = 0.8


            for i in 'PM1 PM3 PM2.5 PM10'.split()[::-1]:
                if i in dfp.columns: 
                    # print(i)
                    try: 
                        ax = dfp.plot(kind='scatter',x='hour', y=i, c='UNIXTIME',colormap='viridis',ax=ax,colorbar=False,label=i, s = sizes[i],alpha = alpha)
                    except:
                        ax = dfp.plot(kind='scatter',x='hour', y=i, c='UNIXTIME',colormap='viridis', label=i, s = sizes[i],alpha=alpha)
                        
                        
            plt.legend()
            plt.tight_layout()
            plt.xlabel('HOUR')
            plt.ylabel('Avg value')
            
            '''
            save to a base 64str
            '''
            import base64
            import io
            IObytes = io.BytesIO()    
            plt.savefig(IObytes,  format='png')
            plt.close()
            IObytes = base64.b64encode(IObytes.getvalue()).decode("utf-8").replace("\n", "")
            plot = html.Img(src="data:image/png;base64,{}".format(IObytes))


            return None,[md('# A grouped summary of the following dataframe:'),br,br,table(dfp.describe().reset_index(),'descplot'), br,br,plot],None


        elif activetabs == 'map_tab': 

            dfp = df['LAT LON'.split()].dropna(subset=['LON']).sample(1000)

            print(dfp)
            
            
            desc = md('''
            # Location overview  
            An interactive map showing a *random* subset of *1000* datapoints from the selected subset. 
            These vary between each initiation due to the above reason. 
            
            The centre of the map is calculated by taking the median latitude and Longitude, the colour shows the time of day, and the tooltip produces the index value from the dataset. 
            ''')
            
            
            log.critical('Known: -ves on Longitude are lost!!!!!')

            
            mid = (dfp.LAT.median(), -dfp.LON.median())
            
            dfp.columns = ['lat','lon']
            
            print(mid)
            
            cc = [dl.CircleMarker( dl.Tooltip(str(row[0])), center=(row[1].lat,-row[1].lon), radius=5, stroke=True,color='none',weight=0,fillColor='blue' ) for row in dfp.iterrows()]
            circles = dl.LayerGroup(cc,id='markers')


            ''' when the regeneratorRuntime issue is solved '''
            log.critical(' Known: cannot show superCluster due to regeneratorRuntime issue')
            # ll = dlx.dicts_to_geojson(dfp.to_dict('records'))
            # 
            # # markers = dl.GeoJSON(data=ll, cluster=True, zoomToBoundsOnClick=True,
            # #        # superClusterOptions={"radius": 100}
            # #        )
            # markers = []
                     


        
            plot =  html.Div(
                id="bibmap",
                children=[ desc,br,br,
                

                
                dl.Map([dl.TileLayer(),circles], center=mid, zoom=12,style={'width': '90vw', 'height': '50vh'})

            
            ],
            
            # style={'width': '100vw', 'height': '50vh', 'margin': "auto", "display": "block"}
            )
            

            return None,None,plot

        




        else:
            return None,None,None

    else:
        return None,None,None







# 
# '''
# app.layout = html.Div([
#     dcc.Location(id='url'),
#     html.Div(id='viewport-container')
# ])
# 
# app.clientside_callback(
#     """
#     function(href) {
#         var w = window.innerWidth;
#         var h = window.innerHeight;
#         return {'height': h, 'width': w};
#     }
#     """,
#     Output('viewport-container', 'children'),
#     Input('url', 'href')
# )
# '''










'''
start Application
'''
if __name__ == '__main__':
    
    # webbrowser.open("http://127.0.0.1:8050")
    from threading import Thread
    
    def openbrowser():
        import webbrowser
        time.sleep(5)
        webbrowser.open("http://127.0.0.1:8050")
        return True
    
    Thread(target = openbrowser).start()
    log.info('\n\n --- opening browser at http://127.0.0.1:8050 ---\n\n')
    
    app.run_server(debug=True)
    