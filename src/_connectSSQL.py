'''
Created on 9 Aug 2018

@author: ostlerr
@author: castells

ran on its own, it lists
This code lists the datasets in the database: you choose the one you want to process and it saves the Schema json in the relevant 
folder prepared in your staging area. See config.ini to set the staging area. 

This is used in CData to process the same thing for datasets and documents 

'''

#import pyodbc
import configparser
import pyodbc
import collections

def connect():
    """Function to connect to the datasource"""
    conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=U:\website development\accessTools\timeline.accdb;')    
    return conn




def processResult(cur):
    pass
    
if __name__ == '__main__':
    cnx = connect()
    
    cur = cnx.cursor()
    cur.execute("""select title, URL  from metadata_document""")
    results = cur.fetchall() 
    resultObj1 = processResult(cur)
    # Declaring namedtuple()   
    for row in results:
        
        trow = resultObj1(*row)
        
        print (trow.title)
    
   