import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from .mdtext import *
import dash_table,dash
import time


br = html.Br()
center = {'margin':'auto','pad':'30px'}

def hidden(hid):
    return html.Div(id='h_'+hid, style={'display':'none'}, n_clicks=0)


  


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

    
    

def multiselect(names):
    
    return dbc.Row([
    itemselect,
    dcc.Dropdown(
        options=[
            {'label': i, 'value': i} for i in names
        ],
        multi=True,
        value="UNIXTIME",
        style={'width':'100%'},
        id = 'itemselect'
    )  
    ])
    


def postparse(contains):
    
    return dbc.FormGroup(
    [
        # dbc.Label("--- Additional Computation ---"),
        additional_checkboxes 
        ,
        dbc.Checklist(
            options=[
            {"label": "Calculate Locations", "value": 'get_loc', "disabled": 'LOC' not in contains},
            {"label": "Return Bins", "value": 'get_bins', "disabled": 'BINS' not in contains},
            {"label": "Include Static Results", "value": 'get_all'},
            {"label": "Anonymise (Skips Serial)", "value": 'anon'},
            {"label": "GroupBy Hour", "value": 'group'},
            ],
            value=[],
            id="post_process",
            switch=True,
            style=center
        ),
    ]
    )

def button(id,name,clr='primary',disabled=False):
    
    stl = {'visibility':'visible'}
    if disabled: stl = {'visibility':'hidden'}
    
    return dbc.Button([dbc.Spinner(size="sm",children=[html.Div(id= id+'_spinner'),name]) ], color=clr, block=True, id = id, outline = True, className="mr-1",style = stl )

      
