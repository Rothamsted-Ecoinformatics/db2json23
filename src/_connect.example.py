'''
Created on 9 Aug 2018

@author: ostlerr
@author: castells

ran on its own, it lists
This code lists the datasets in the database: you choose the one you want to process and it saves the Schema json in the relevant 
folder prepared in your staging area. See config.ini to set the staging area. 

This is used in CData to process the same thing for datasets and documents 

'''

import pyodbc
import collections

def connect():
 
    #con = pymysql.connect(host = host,user=user,password=pwd,db=db,cursorclass=pymysql.cursors.DictCursor) 
    dsn='saved-odbc-connection-name'
    uid='dbUN'
    pwd='dbPWD'    
    con  = pyodbc.connect('DSN='+dsn+';uid='+uid+';pwd='+pwd)
    
    return con

def getCursor():
    con = connect()
    cur = con.cursor()
    return cur
    
if __name__ == '__main__':
    cnx = connect() 
    cur = cnx.cursor()
    cur.execute("""select title, URL  from metadata_documents""")
    results = cur.fetchall()  
    # Declaring namedtuple()   
    for row in results:      
        print ('\nTitle = '  + row.title + '\nURL   = '+row.URL)

    print (results)
   