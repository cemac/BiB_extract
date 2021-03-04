import dash_core_components as dcc

def md(txt,id=''):
  return dcc.Markdown(txt,id=id)
  
header = md('''
# BiBSensor Database browser

This is a simple browser and plotter app for the Born in Bradford Portable Sensor database. 
''')  

timein = md('''

#### Time inputs
Please select a date range from the calandar view below: `start date` -> `end date`

''')  

itemselect = md('''
#### Select / Remove Columns you are interested in. 

- The UNIXTIME column will always be selected.
- If you plan on using locations, select the 'calculate locs' checkbox
- If you require bins, you do **NOT** need to select the column from here. **INSTEAD** tick the 'return bins' checkbox 
- Remember to **_select the measurement_** columns you are interested in e.g PM1,PM10 etc. 
''')

additional_checkboxes =     md('''

    #### Additional Options
    Additional postprocessing of the dataset. Some options may add/remove additional columns in the SQL query. 
    
    These are the calculation of `GeoLocation`, Returning the `Bins`, Including `ALL` sensor types and removing of the `SERIAL` column
    ''') 
    
instructions = '''
### **To extract the dataset**
1. Precompute values (see button below)
2. If happy, extract dataset. *This allows browsing on table tab* 
3. Optional- download the data as a csv *(Not advised for large datasets)*


'''


introtab =  md('''
## Instructions 

*Before using please read the README page* 

A general overview of the dataset is provided below.
- To filter data use the `Filter Parameters` tab
- Once done the data can be viewed using the additional tabs; e.g. `View Table`
''')





