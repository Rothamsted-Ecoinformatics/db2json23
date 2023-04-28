"""@package image2json
Created on 11 June 2019

@author: castells
@description: Use this tool to list all the _metadata for an experiment. Saves in the proper metadata folder. 

It connects to the mssqdl database, lists the experiments that have _dmetadata in them and then asks to either do one or do all

When the type is a document: treat it differently... 

"""
import sys
import pyodbc
import json
import settings
import _metadata
import _connect
from _overlapped import NULL




class Dataset:
    """The class that will define a single dataset . The row is the result of a query in the table
    """
    def __init__(self, row):
        self.md_id = row.md_id 
        self.title = row.title 
        self.URL = row.url  
        self.identifier = row.identifier 
        self.identifier_type = row.identifier_type 
        self.dataset_type = row.dataset_type 
        self.extension = row.document_format_id 
        self.description = row.description_abstract
        self.fieldname = row.fieldname 
        self.experiment_name = row.experiment_name 
        self.publication_year = row.publication_year
        self.experiment_code = row.experiment_code 
        self.shortName = row.short_name
        self.isReady = row.is_ready
        self.isExternal = row.is_external if row.is_external else 0
        self.grade = row.grade if row.grade else 1
        self.dstype = row.dstype if row.dstype else 'N/A'
        
        if row.version is None: 
            self.version = "01"
        else: 
            if int(row.version) <10:
                self.version = '0'+str(row.version).lstrip('0')
            else: 
                self.version = row.version
        
    def asdatasetJson(self):    
        dataset =  {         
              "md_id": self.md_id,
              "title": self.title,
              "URL": self.URL,
              "identifier": self.identifier,
              "identifier_type":   self.identifier_type,
              "dataset_type": self.dataset_type,
              "extension": self.extension,
              "description": self.description,
              "fieldname": self.fieldname,
              "experiment_name": self.experiment_name,
              "experiment_code": self.experiment_code,
              "grade":self.grade,
              "dstype": self.dstype,
              "publication_year": self.publication_year,
              "version": self.version,
              "isReady":self.isReady,
              "isExternal":self.isExternal,
              "shortName":self.shortName if self.shortName else 'N/A',
              "UID": self.version+"-"+self.shortName if self.shortName else self.md_id                   
            }        
        return dataset
    
    
def allDatasets():
    cnx = _connect.connect()
    cur = cnx.cursor()
    lsAllDatasets =  []
    sql = ''
    sql = 'select * from vw_metadata_documents  where grt_value = \'Dataset\' and  is_ready >= 1 order by  title asc'
    
    # sql =       'SELECT m.id as md_id, title, url, identifier, identifier_type, dataset_type as dstype, grt.type_value  as grt_value, '
    # sql = sql + ' srt.type_value  as dataset_type,  document_format_id, description_abstract, e.field_id, f.name as fieldname,'
    # sql = sql + ' e.name as experiment_name, e.code  as experiment_code, publication_year, short_name, publisher_id, is_ready, '
    # sql = sql + ' is_external, o.name as publisher, version,  lang,  grade, is_external,  doi_created'
    # sql = sql + ' FROM metadata_documents m'
    # sql = sql + ' join experiments e on m.experiment_id = e.id'
    # sql = sql + ' join fields f on e.field_id = f.id'
    # sql = sql + ' join organisations o on o.id = m.publisher_id'
    # sql = sql + ' join general_resource_types grt on grt.id = m.general_resource_type_id '
    # sql = sql + ' join specific_resource_types srt on srt.id = m.specific_resource_type_id'
    # sql = sql + ' where grt.type_value = \'Dataset\' and  is_ready  >= 1 order by  title asc'
    print("debug CData ln 96")
    print(sql)
    cur.execute(sql)
    results = cur.fetchall()  
    for row in results: 
        dt = Dataset(row)        
        lsAllDatasets.append(dt.asdatasetJson()) 
        _metadata.makeDocumentInfo(str(dt.md_id)) 
    return lsAllDatasets

def makeAllDatasetList():
    
    lsDatasets = allDatasets()
    xname = settings.STAGE+ "metadata/default/datasets.json"
    fxname = open(xname,'w+')
    strDatasets =  json.dumps(lsDatasets, indent=4)
    print (strDatasets)
    fxname.write(strDatasets)
    fxname.close()
    print('list of datasets saved in '+xname)

def getDatasets(typeOfDoc = 'Dataset', expt_code = 'R/BK/1'):
    cnx = _connect.connect()
    cur = cnx.cursor()
    lsDatasets =  []
    
    sql = 'select * from vw_metadata_documents  where grt_value = \'{}\' and  experiment_code = \'{}\' order by grade desc, title asc'.format(typeOfDoc, expt_code)
    #print("debug _metadata 122")
    #print(sql)
    cur.execute(sql)
    results = cur.fetchall() 

    for row in results: 
        dt = Dataset(row)        
        lsDatasets.append(dt.asdatasetJson()) 
        _metadata.makeDocumentInfo(str(dt.md_id)) 
    print(lsDatasets)
    return lsDatasets


def makeDatasetList(typeOfDoc,expt_code):
    
    lsDatasets = getDatasets(typeOfDoc,expt_code)
    #debug _metadata 137
    print(lsDatasets)
    folder = ''.join(ch for ch in expt_code if ch.isalnum()).lower()
    xname = settings.STAGE+ "metadata/"+str(folder)+"/"+typeOfDoc.lower()+"s.json"
    fxname = open(xname,'w+')
    strDatasets =  json.dumps(lsDatasets, indent=4)
    #debug _metadata 143
    print(strDatasets)
    fxname.write(strDatasets)
    fxname.close()
    print('list of '+typeOfDoc+' saved in '+xname)
    
    
def getExptCodes(typeOfDoc):
    #list 
    expts_codes = []
    cnx = _connect.connect()
    cur = cnx.cursor()
    sql = """select distinct e.code code
    from metadata_documents md join experiments e on md.experiment_id = e.id
    join general_resource_types grt on md.general_resource_type_id = grt.id
    where grt.type_value  like \'{}\' order by code""".format(typeOfDoc)
    # sql = ''
    # sql = sql + ' select DISTINCT e.code code '
    # sql = sql + ' from metadata_documents md join experiments e on md.experiment_id = e.id'
    # sql = sql + ' join general_resource_types grt on md.general_resource_type_id = grt.id'
    # sql = sql + ' where grt.type_value like \'{}\''
    # sql = sql + ' order by code'
    # sql = sql.format(typeOfDoc)

    cur.execute(sql)
    results = cur.fetchall()  
    counter = 0  
    for row in results: 
        
        counter +=1  
        expts_codes.append(row.code)
           
        
    return expts_codes 



if __name__ == '__main__':
    print('This will create the metadata for the datasets in selected experiments. At the end, it will also compile the keywords.')
    print('  ')
    try:   
        while True:
            expt = ''
            
            typeOfDoc = '0'
            
            while typeOfDoc == '0':
                answer = input('Texts (T) or Datasets (D)?').lower()
                print(answer)
                if answer not in ['t', 'd']:
                    print ('t or d please')
                else:
                    typeOfDoc = 'Text' if answer == 't' else 'Dataset'
                
            exptCodes = getExptCodes(typeOfDoc)
       
            IDs = []     
            tokens = ['a']
            counter = 0
            for items in exptCodes: 
                counter = counter + 1
                print ("%s :  %s  " % (counter, items))
                tokens.append(str(counter))
            print (" ")  
            print(tokens)
        
            token = '0'
            while token == '0':
                print("   ")   
                token = input('Which Experiment Code (a for all)?').lower()
                print(token)
                masterCopy = []
                if token  not in tokens:
                    print("not in the list")
                    token = '0'
                else: 
                    if token != 'a':
                        inToken = int(token)
                        inToken = inToken - 1
                        exptCode = exptCodes[inToken]
                        print (exptCode)
                        makeDatasetList(typeOfDoc,exptCode)
                        
                    else:
                        for exptCode in exptCodes:
                            makeDatasetList(typeOfDoc,exptCode)
                            
                          
                   
             
            print("   ")   
            new_game = input("Would you like to do another one? Enter 'y' or 'n' ")
            if new_game[0].lower()=='y':
                playing=True
                continue
            else:
                print("--- Compiling All Datasets --- ")
                makeAllDatasetList()
                print("   ")
                print("   ")
                print("   ")
                print("Thanks for your work!")
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
        


    
    
    
    