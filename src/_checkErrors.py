'''
Created on 9 Aug 2018

@author: ostlerr
@author: castells

ran on its own, it lists
This code lists the datasets in the database: you choose the one you want to process and it saves the Schema json in the relevant 
folder prepared in your staging area. See settings to set the staging area. 

This is used in CData to process the same thing for datasets and documents 

'''
import sys

import json

import settings
import AFolder
import _connect

def getDOIs():
    cnx = _connect.connect()
    cur = cnx.cursor()
    lsKW =  []
    
    sql = 'select distinct s.subject, s.subject_uri, ss.schema_name, ss.schema_uri  '
    sql += ' from subjects s  '
    sql += ' join subject_schemas ss on s.ss_id = ss.ss_id '
    sql += ' inner join document_subjects ds on ds.subject_id = s.subject_id'
    sql += ' order by subject asc'

    cur.execute(sql)
    results = cur.fetchall()  
    for row in results: 
        kw = Keyword(row)        
        lsKW.append(kw.askwJson()) 
    return lsKW


    
if __name__ == '__main__':
    try:
        #-28178770 is a dataset
        #-1140916605 has author
        # 4 is a text 
    
        
        while True:
            datasetID = 0
            DOCIDs = getDOCIDs()
            IDs = []     
            tokens = []
            counter = 0
            for items in DOCIDs: 
                counter = counter + 1
                #print ("%s -  %s (%s) DOCIDs =  %s" % (counter, items['title'],items['expCode'], items['documentID']))
                IDs.append(str(items['documentID']))
                tokens.append(str(counter))
            #print (" ")  
            #print(tokens)   
            token = '0'
            while token == '0':
                token = input('Which dataset? ')
                #print(token)
                if token  not in tokens:
                    #print("not in the list")
                    token = '0'
                else: 
                    inToken = int(token)
                    inToken = inToken - 1
                    datasetID = IDs[inToken]
                #print (datasetID)
            
           
            new_game = input("Would you like to do another one? Enter 'y' or 'n' ")
            if new_game[0].lower()=='y':
                playing=True
                continue
            else:
                #print("Thanks for your work!")
                break    
           
          
    #     documentInfo.mdId = input('Enter Document ID: ')
    #     documentInfo = process(documentInfo)    
    #     save(documentInfo)         
    
    
            
    
    except:
        print("Unexpected error:", sys.exc_info()[0])        
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        print(sys.exc_info()[2].tb_lineno)
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                             sys.exc_info()[1],
                                             sys.exc_info()[2].tb_lineno))
    

