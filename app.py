'''
The main app used to access the merged sensor database 

Author: D. Ellis, d.ellis@-nospam-@leeds.ac.uk @CEMAC

'''



''' 
Constants
'''
__DBLOC__ = 'merged.db'
## change database location as required. This presumes that it is located within the current directory. 



'''
Imports
'''
import dash,sqlite3,sys
import dash_daq as daq
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd

from process_scripts import log_manager
from process_scripts.components import *
from process_scripts.mdtext import *
'''
Additional Setup
'''
if sys.version[0]!= '3':
	sys.exit('You are not using python 3 - ** sadface **')
    
log = log_manager.getlog(__name__)
info = log.info

info('Loading Database')
conn = sqlite3.connect('merge.db')

dblength = conn.execute("SELECT COUNT() from MEASUREMENTS").fetchone()[0]
info('Database length:'+ str(dblength))

"PRAGMA table_info(MEASUREMENTS)"

info('Column Names\n')
cols = pd.read_sql_query("PRAGMA table_info(MEASUREMENTS)", conn).name.values
info(cols)


info('Calculating time range...')
dbrange = pd.to_datetime([conn.execute("SELECT %s(UNIXTIME) from MEASUREMENTS"%i).fetchone()[0] for i in ['MIN','MAX']],unit='s')
info('Min-Max Datetime:' + str(dbrange.astype(str).values))


background = pd.DataFrame([['Start Date',dbrange[0]],['End Date',dbrange[1]],['No Items',dblength],['columns',' | '.join(cols)]],columns = ['Name','Value'])




''' 
Main Application
'''
external_stylesheets = [dbc.themes.COSMO]#'https://codepen.io/anon/pen/mardKv.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

'''
Layout

https://bootswatch.com/cosmo/
'''


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
                postparse(cols)
            ],)

rightcol= dbc.Col(
            style = center,
            align="center",
            children = [
            multiselect(cols)
            ],)


'''
TABS
'''
tab = dbc.Card(
    dbc.CardBody(
    [
        dbc.Row([   md('## Instructions '),
        br,br, table(background,'info_table',{'width':'80%','margin':'auto'})]),
        br,br,
        dbc.Row([leftcol,rightcol]),
    ] # selection row
    ),
    className="mt-3",
)


#### TABLE
tab_table = dbc.Card(
    dbc.CardBody(            
    
        br,
        #loading(html.Div(id='otherinfo'))
        

    
    ),
    className="mt-3",
)


# LINEPLOT
tab_lineplot = dbc.Card(
    dbc.CardBody(            
    
        br,
        #loading(html.Div(id='otherinfo'))
    ),
    className="mt-3",
)
    
tab_leaflet = dbc.Card(
    dbc.CardBody(            
    
        br,
        #loading(html.Div(id='otherinfo'))
    ),
    className="mt-3",
)
    

tabs = dbc.Tabs(
    [
        dbc.Tab(tab, label="Filter Parameters"),
        dbc.Tab(tab_table, label="View Table"),
        dbc.Tab(tab_lineplot, label="View Scatter"),
        dbc.Tab(tab_leaflet, label="View Map",disabled=True),

    ]
)


'''
APP LAYOUT
'''
app.layout = html.Div(
style=center,
 children = [

        bginfo,br,# first row
        
        tabs
    
        
        
])


'''
Functions on change
'''


@app.callback(
    dash.dependencies.Output('otherinfo', 'children'),
    [dash.dependencies.Input('date', 'start_date'),
     dash.dependencies.Input('date', 'end_date')])
def update_output(start_date, end_date):
    string_prefix = 'You have selected: '
    # if start_date is not None:
    #     start_date_object = date.fromisoformat(start_date)
    #     start_date_string = start_date_object.strftime('%B %d, %Y')
    #     string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    # if end_date is not None:
    #     end_date_object = date.fromisoformat(end_date)
    #     end_date_string = end_date_object.strftime('%B %d, %Y')
    #     string_prefix = string_prefix + 'End Date: ' + end_date_string
    # if len(string_prefix) == len('You have selected: '):
    #     return 'Select a date to see it displayed here'
    # else:
    #     return string_prefix



'''

update global dictionary on change of each item 


on click of button, 

download 

'''






'''
start Application
'''
if __name__ == '__main__':
    app.run_server(debug=True)