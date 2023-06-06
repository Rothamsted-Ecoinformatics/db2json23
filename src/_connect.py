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
 
    # #con = pymysql.connect(host = host,user=user,password=pwd,db=db,cursorclass=pymysql.cursors.DictCursor) 
    # #Connection for Sandpit
    # dsn='burdock-eraSandpit'
    # uid='trampolines'
    # pwd='Ad0rnSp4d3'    
    # con  = pyodbc.connect('DSN='+dsn+';uid='+uid+';pwd='+pwd)
    
    # connection for Gilbert
    dsn='burdock-eraGilbert'
    uid='bellringer'
    pwd='G3n3tL30n3'    
    con  = pyodbc.connect('DSN='+dsn+';uid='+uid+';pwd='+pwd)
    
    
    
# DB_CONNECTION=sqlsrv
# DB_HOST=burdock2.rothamsted.ac.uk
# DB_PORT=1433
# DB_DATABASE=eraGilbert
# DB_USERNAME=bellringer
# DB_PASSWORD=G3n3tL30n3

    
    #con = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\castells\Rothamsted Research\e-RA - Documents\datacite\DataCite Metadata database.accdb;')
    #con = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=D:\code\access\DataCite Metadata database.accdb;')
    return con

def getCursor():
    con = connect()
    cur = con.cursor()
    return cur

# def connect():
#     
#     # ERA database
#     erahost = 'localhost'
#     erauser = 'root'
#     erapwd= ''
#     eradb = 'cdera'
#     eraCon = pymysql.connect(host=erahost,user=erauser,password=erapwd,db=eradb,cursorclass=pymysql.cursors.DictCursor)
#     
#     return eraCon




    
if __name__ == '__main__':
    cnx = connect() 
    cur = cnx.cursor()
    cur.execute("""select title, url  from metadata_documents""")
    results = cur.fetchall()  
    # Declaring namedtuple()   
    for row in results:      
        print ('\nTitle = '  + row.title + '\nURL   = '+row.url)

    print (results)
   