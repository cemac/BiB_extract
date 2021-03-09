from bib_cli import *

import dash
import dash_html_components as html
import dash_leaflet as dl
import sys
from process_scripts import log_manager
log = log_manager.getlog(__name__)
info = log.info
import argparse
parser = argparse.ArgumentParser()


parser.add_argument('-i',"--info", dest='info', 
                help="Get Database Information Overview", action='store_true')
                
parser.add_argument('-t',"--type", dest='type', type=int,
                help="Sensor Type to extract", default=2)

parser.add_argument('-s', '--start', nargs='?', type=str, default='usefirst', help='Start Time in format "YYYY-MM-DD HH:MM" ')
# run bib_cli.py -s "2010-19-02 11:34"

parser.add_argument('-e', '--end', nargs='?', type=str, default='uselast', help='End Time in format "YYYY-MM-DD HH:MM" ')


parser.add_argument('-x',"--limit", dest='limit', type=int,
                help="How many values to extract", default=-99)


parser.add_argument('--dbloc', nargs='?', type=str, default='', help='Set an alternative database location')


parser.add_argument('--size', nargs='?', type=str, default='PM10', help='Column to use for node size" ')


args = parser.parse_args()
info(args)
'''
Main code
'''
args.cols='*'
args.info=args.dry=False
args.save=''
args.loc=True
SQL,df = clirun(args)

    
bins={
'PM10':[54.,154.,254.,354.,424.,604.],
'PM3':[15,40,65,150,250,500],
'PM2.5':[15,40,65,150,250,500],
'PM1':[100]
}
    
cols = 'green yellow orange red purple brown'.split()
    
def setcat(mybins,val):
    for i,j in enumerate(mybins):
        print(i,val<j,val,j)
        if val<j:
            return int(i)


'''https://www.researchgate.net/publication/268057874_AIRNow_AIR_QUALITY_NOTIFICATION_AND_FORECASTING_SYSTEM/figures?lo=1
'''


    
df.LON*= -1
df.dropna(subset=['LON'], inplace=True)

mid = [df.LAT.median(), df.LON.median()]
print (mid)
what = args.size

mx = df[what].max()

mybins = bins[what]
df['cat'] = [setcat(mybins,k) for k in df[what].values]

print (df.head(5),df[['cat',what]].describe)

#print (help(dl.Circle))
'''
Keyword arguments:
 |  - children (a list of or a singular dash component, string or number; option
al): The children of this component
 |  - center (list of numbers; required): The center of the circle (lat, lon)
 |  - radius (number; required): Radius of the circle, in meters.
 |  - stroke (boolean; optional): Whether to draw stroke along the path. Set it 
to false to disable borders 
 |  on polygons or circles.
 |  - color (string; optional): Stroke color
 |  - weight (number; optional): Stroke width in pixels
 |  - opacity (number; optional): Stroke opacity
 etc... 
'''

markers = [dl.CircleMarker( dl.Tooltip(str(row)), center=[row[1].LAT, row[1].LON], radius=25*row[1][what]/mx, stroke=True,weight=1,color='red', fillColor=cols[row[1]['cat']],fillOpacity=0.7) for row in df.iterrows()]

#fillColor
#color fillOpacity

app = dash.Dash()
app.layout = html.Div(
id="BornInBradford",
    children=
    dl.Map([dl.TileLayer(),dl.LayerGroup(markers,id='markers')],    
           center=mid, zoom=13,
           style={'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"})
)

if __name__ == '__main__':
    app.run_server(debug=True)