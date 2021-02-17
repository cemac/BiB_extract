import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import time


br = html.Br()
center = {'margin':'auto','pad':'30px'}

def md(txt):
  return dcc.Markdown(txt)
  


def loading(children):
    return dcc.Loading(
            id="spinner",
            type="default",
            children=children
        )
        

def table(df,tid,style={'width':'100%'}):
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True,responsive=True, id=tid, style=style)
    
    
def daterange(dt, app):

    
    return dcc.DatePickerRange(
        id='date',
        min_date_allowed=dt[0],
        max_date_allowed=dt[1],
        initial_visible_month=dt[0],
        display_format='D/MM/YYYY',
        calendar_orientation='horizontal',
        start_date=dt[0],
        end_date=dt[1],
        style = center,
        with_portal=True,
    )



    @app.callback(Output("otherinfo", "children"), Input("date", "start_date"))
    def spin(value):
        time.sleep(5)
        return value +'dfsdf'
    
    

def multiselect(names):
    
    return dbc.Row([
    md('''
    #### Select / Remove Columns you are interested in. 
    
    - The UNIXTIME column will always be selected.
    - If you plan on using locations, select the 'calculate locs' checkbox
    - Similarly if you require bins, select the 'get bins' checkbox. 
    '''),
    dcc.Dropdown(
        options=[
            {'label': i, 'value': i} for i in names
        ],
        multi=True,
        value="UNIXTIME",
        style={'width':'100%'},
    )  
    ])
    


def postparse(contains):
    
    return dbc.FormGroup(
    [
        # dbc.Label("--- Additional Computation ---"),
        md('''

        #### Additional Options
        Additional postprocessing of the dataset. Some options may add/remove additional columns in the SQL query. 
        
        These are the calculation of `GeoLocation`, Returning the `Bins`, Including `ALL` sensor types and removing of the `SERIAL` column
        ''')  
        ,
        dbc.Checklist(
            options=[
            {"label": "Calculate Locations", "value": 'loc', "disabled": 'LOC' not in contains},
            {"label": "Return Bins", "value": 'bins', "disabled": 'BINS' not in contains},
            {"label": "Include Static Results", "value": 'sensor', 'checked':True},
            {"label": "Anonymise (Skips Serial)", "value": 'serial'},
            {"label": "GroupBy Hour", "value": 'group'},
        
            
            ],
            value=[],
            id="post_process",
            switch=True,
            style=center
        ),
    ]
    )



      
