"""@package image2json
Created on 11 June 2019

@author: castells
@description: Use this tool to list all the _metadata for an experiment. Saves in the proper metadata folder. 

It connects to the mssqdl database, lists the experiments that have _dmetadata in them and then asks to either do one or do all

When the type is a document: treat it differently... 

"""
import sys
import pyodbc
import csv
import json
import settings
import _metadata
import _connect
from _overlapped import NULL



class Keyword:
    """The class that will define a single keyword . The row is the result of a query in the table
    select s.subject, s.subject_uri, ss.schema_name, ss.schema_uri 
    from subjects s
    join subject_schemas ss on s.ss_id = ss.ss_id 
    order by subject asc
     "datasets" :  getDS(self.subject)  
     "datasets" : getDS(self.subject) identifier  """
    def __init__(self, row):
     
        self.subject = row.subject 
        self.schema = row.name 
        self.identifier= row.suburi 
        self.schema_uri = row.schemauri
        
        
        
    def askwJson(self): 
           
        keyword =  {         
              "keyword": self.subject,
              "identifier": self.identifier,
              "schema":   self.schema,
              "URL": self.schema_uri + self.identifier,
              "datasets" :  getDS(self.subject),
              "documents": getDOCS(self.subject),
              "pages" :getPAGES(self.subject)
              
                                         
            }        
        return keyword
    
def getPAGES(kw):
    print(kw)
    lsPAGES = []
    
    # for the files in the lists: open the files in turn Try with 1
    # the list of pages: 
    with open('d:/eRAWebStage/eraGilbert01/metadata/default/infofiles.json', 'r') as myfiles:
        files=myfiles.read()
        
    obj = json.loads(files)
    for fileItem in obj:
        # "Credit": "eRA curators",
        # "FileName": "index",
        # "Type": "html",
        # "Caption": "Brooms Barn Met Station ",
        # "exptID": "bms",
        # "link": "http://local-info.rothamsted.ac.uk/eRA/era2018-new/info/bms/index",
        # "isReviewed": 0
        #P:\era2018-new\metadata\met/
        if obj[fileItem]['isReviewed'] == '1':
            fileString = "P:\\\\era2018-new\\metadata\\"+obj[fileItem]['exptID']+"\\"+obj[fileItem]['FileName']+'.'+obj[fileItem]['Type']
            try: 
                file1 = open(fileString, "r")
               # setting flag and index to 0
                flag = 0
                index = 0
                # Loop through the file line by line
                for line in file1:  
                    index += 1 
                  
                # checking string is present in line or not
                    if kw.lower() in line.lower():
                        flag += 1 
                        break
                      
                # checking condition for string found or not
                if flag == 0: 
                    pass
                    #print('String', kw , 'Not Found') 
                else: 
                    print("Found in  " + fileString) #
                    URL = 'info/'+obj[fileItem]['exptID']+'/'+obj[fileItem]['FileName']
                    title = obj[fileItem]['Caption']
                    exptID = obj[fileItem]['exptID']
                    
                    pageInsert = dict( 
                            URL = 'info/'+obj[fileItem]['exptID']+'/'+obj[fileItem]['FileName'],
                            title = obj[fileItem]['Caption'],
                            pageType = obj[fileItem]['pageType'],
                            exptID = obj[fileItem]['exptID']
                            )
                    print(pageInsert)
                    lsPAGES.append(pageInsert)
          
                # closing text file
                   
                file1.close()
            except:
                pass
                #print("File not Found " + fileString)
    print(lsPAGES)
    return  lsPAGES
   
def getDS(kw):
    cnx = _connect.connect()
    cur = cnx.cursor()
    lsDS = []
    #select the keywords and the md_ids associated with that
    sql = ''' select s.subject as subject, md.id , md.title, md.identifier, md.url,md.short_name, md.version, e.code 
     from subjects s
     inner join document_subjects ds on ds.subject_id = s.id 
     join metadata_documents md on md.id = ds.metadata_document_id 
     join experiments e on md.experiment_id = e.id 
     where md.general_resource_type_id = 4
     and subject like '{}'  order by subject asc'''.format(kw)
    
    cur.execute(sql)
    results = cur.fetchall()  
    for row in results:
        DS = row.id
        if DS:
            
    
    
            version = float(row.version)
            if int(version) < 10:
                strCount = '0'+str(version)
            else:
                strCount = str(version)

            exptCode = ''. join(ch for ch in row.code if ch.isalnum()).lower()
            lsDS.append(dict( 
                DOI = row.identifier,
                URL = 'dataset/'+exptCode+'/'+strCount+'-'+row.short_name,
                title = row.title,
                exptID = exptCode
                )
            )
    print(lsDS)        
    return lsDS 

def getDOCS(kw):
    cnx = _connect.connect()
    cur = cnx.cursor()
    lsDS = []
    #select the keywords and the md_ids associated with that
    sql = ''' select s.subject as subject, md.id , md.title, md.identifier, md.url,md.short_name, md.version, e.code 
     from subjects s
     inner join document_subjects ds on ds.subject_id = s.id 
     join metadata_documents md on md.id = ds.metadata_document_id 
     join experiments e on md.experiment_id = e.id 
     where md.general_resource_type_id = 12
     and subject like '{}'  order by subject asc'''.format(kw)
    
    cur.execute(sql)
    results = cur.fetchall()  
    for row in results:
        DS = row.id
        if DS:
            version = float(row.version)
            if int(version) < 10:
                strCount = '0'+str(version)
            else:
                strCount = str(version)

            exptCode = ''. join(ch for ch in row.code if ch.isalnum()).lower()
            lsDS.append(dict( 
                DOI = row.identifier,
                URL = row.url,
                title = row.title,
                exptID = exptCode 
                )
            )
    return lsDS   


def getKeywords():
    cnx = _connect.connect()
    cur = cnx.cursor()
    lsKW =  []
    
    sql = '''select distinct s.subject, s.uri as suburi, ss.name, ss.uri as schemauri 
     from subjects s  
     join subject_schemas ss on s.subject_schemas_id = ss.id 
     inner join document_subjects ds on ds.subject_id = s.id
     order by subject asc'''

    cur.execute(sql)
    results = cur.fetchall()  
    for row in results: 
        kw = Keyword(row)        
        lsKW.append(kw.askwJson()) 
    return lsKW



def makeKeywordList():
    print('Indexing Keywords. Please be patient. Ensure that the infofile.json list is up-to-date. ')
    lsKW = getKeywords()
    
        
    xname = settings.STAGE+ "metadata/default/keywords.json"
    fxname = open(xname,'w+')
    strKW =  json.dumps(lsKW, indent=4)
    # print (strKW)
    fxname.write(strKW)
    fxname.close()
    print('List of keywords  is saved in '+xname)
    print('')
    print('')
    
def make_json(csvFilePath, jsonFilePath, Key):
    
    # create a dictionary
    data = {}
    print(Key)
    # Open a csv reader called DictReader
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        
        # Convert each row into a dictionary
        # and add it to data
        for rows in csvReader:
            
            # Assuming a column named 'id' to
            # be the primary key
            key = rows[Key]
            data[key] = rows

    # Open a json writer, and use the json.dumps()
    # function to dump data
    print(data)
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))
        print('saved in '+jsonFilePath)

if __name__ == '__main__':
    #first we update the infofiles file from the latest and update biblio as we are here 
    toConvert = settings.toConvert
        
    for file in toConvert: 
        make_json(toConvert[file]['csvFilePath'], toConvert[file]['jsonFilePath'], toConvert[file]['idKey'])
        # Call the make_json function
        
     
    makeKeywordList()



    
    
    
    