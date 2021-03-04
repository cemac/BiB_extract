'''
{'start_date': 1606922016.0, 'end_date': 1609873220.0, 'start_date_str': '2020-12-02T15:13:36', 'end_date_str': '2021-01-05T19:00:20', 'sliders': [], 'columns': 'UNIXTIME'}
'''

def makesql(params,count=False):
    
    pc = params.copy()
    
    cols = pc['columns']
    sliders = pc['sliders']
    
    if type(cols) == str:
        cols=[cols]
    
    if 'limit' in sliders: pc['limit'] = 'LIMIT 2000'
    else: pc['limit'] = '' 
    
    if 'get_loc' in sliders:
        cols.append('LOC')
        
    if 'get_bins' in sliders:
        cols.append('BINS')
        
    cols = set(cols)    
    if 'anon' in sliders:
        cols -= set(['SERIAL'])
    
    pc['cols'] = ', '.join(list(cols))
    
    
    if 'get_all' in sliders:
        pc['type'] = ''
    else:
        pc['type'] = 'TYPE = 2 and '
    
    
    if count:
        return "SELECT COUNT(UNIXTIME) from MEASUREMENTS where %(type)sUNIXTIME between %(start_date)d and %(end_date)d %(limit)s"%pc
    
    
    return "SELECT %(cols)s from MEASUREMENTS where %(type)sUNIXTIME between %(start_date)d and %(end_date)d %(limit)s"%pc