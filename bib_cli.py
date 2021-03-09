''' 
A script to automate database extraction
'''
__version__ = '0.0.1'
__author__  = 'Daniel Ellis'
__contact__ = 'd.ellis@-nospam-@leeds.ac.uk'

''' 
setup
'''
from config import __DBLOC__, __SAVELOC__, __KEY__

import sys
if sys.version[0]!= '3':
	sys.exit('You are not using python 3 - ** sadface **')

from process_scripts import log_manager
log = log_manager.getlog(__name__)
info = log.info

# print(chr(27) + "[2J", '\n\n') ## clear console using escape characters
info('Importing Libraries')


'''
Imports
'''
import sqlite3
import pandas as pd
from datetime import datetime
from process_scripts.readsql import *
from process_scripts.parameters import  startup
from process_scripts.decode import *

if os.path.isfile(__KEY__): 
    haskey=True
else: 
    log.warning('LOC FILE: %s not found!'%__KEY__)
    haskey=False
    





def clirun(args):
    global __DBLOC__

    if args.start =='usefirst' and args.end=='uselast':
        
        args.dates = ''

    elif args.start==args.end: 
        sys.exit('start and end dates cannot be the same')
    
    elif args.start =='usefirst': # enddate only 
        
        end_date = int((pd.to_datetime(args.end)-datetime(1970,1,1)).total_seconds())
        
        args.dates = 'AND UNIXTIME <= %d'%end_date

    elif args.end =='uselast': # startdate only 
        
        start_date = int((pd.to_datetime(args.start)-datetime(1970,1,1)).total_seconds())
        
        args.dates = 'AND UNIXTIME >= %d'%start_date

    
    else:# we have supplied both
        print(pd.to_datetime(args.start),args.start)
        start_date = int((pd.to_datetime(args.start)-datetime(1970,1,1)).total_seconds())
        end_date = int((pd.to_datetime(args.end)-datetime(1970,1,1)).total_seconds())
        args.dates = 'AND UNIXTIME between %d and %d'%(start_date,end_date)

    if args.limit < 0:
        args.limit='' 
    else:
        args.limit = 'LIMIT %d'%args.limit
                    
    if args.dbloc!='':
        __DBLOC__ = args.dbloc
    
    SQL = "SELECT %(cols)s from MEASUREMENTS where TYPE=%(type)s %(dates)s %(limit)s"%vars(args)        
    
    info('\n\nSQL STRING')
    info(SQL)
    
    if args.dry and not args.info:
        print('\n')
        log.warning('This is a dry run. Stopping here.')
        return SQL, None
    else:    
        
        info('Loading Database')
        conn = sqlite3.connect(__DBLOC__,check_same_thread=False)

        
        if args.info: 
            dblength, cols, dbrange, background, params = startup(conn,info)
            print('\n',background)
            if args.info: return SQL, background
        
        
        df =  pd.read_sql_query(SQL, conn)
        
        conn.close()
        
        df = par_date(df)
        print('\n', df,'\n')
        
        
        if args.loc:
            info('decoding location data')
            df,ctime = par_loc(df.reset_index(),False)
            info(ctime)
            
        
        if args.info:
                sdata = {'Shape':str(df.shape), 'Size in Memory': convert_bytes(sys.getsizeof(df))}
                
                print('\n', sdata)
                
        if args.save != '':
            df.to_csv(args.save)


        return SQL, df



















if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    
    parser.add_argument('-i',"--info", dest='info', 
                    help="Get Database Information Overview", action='store_true')
                    
    parser.add_argument('-t',"--type", dest='type', type=int,
                    help="Sensor Type to extract", default=2)
                                        
    
    parser.add_argument('-s', '--start', nargs='?', type=str, default='usefirst', help='Start Time in format "YYYY-MM-DD HH:MM" ')
    # run bib_cli.py -s "2010-19-02 11:34"
    
    parser.add_argument('-e', '--end', nargs='?', type=str, default='uselast', help='End Time in format "YYYY-MM-DD HH:MM" ')
    
    parser.add_argument('-l',"--loc", dest='loc', 
                    help="Decode Locations", action='store_true')
                    
    parser.add_argument('-c', '--cols', nargs='?', type=str, default='*', help='Chosen Columns (space sep): "UNIXTIME,PM1,PM10,T,RH" ')
    
    parser.add_argument('-x',"--limit", dest='limit', type=int,
                    help="How many values to extract", default=-99)

    
    parser.add_argument('-d',"--dry", 
                    help="Dry Run (dont execute)", action='store_true')
    
    parser.add_argument('--save', nargs='?', type=str, default='', help='Filename and locationpath to save csv: e.g. ./data.csv')
    
    parser.add_argument('--dbloc', nargs='?', type=str, default='', help='Set an alternative database location')
    
    args = parser.parse_args()
    info(args)
    '''
    Main code
    '''
    SQL,df = clirun(args)