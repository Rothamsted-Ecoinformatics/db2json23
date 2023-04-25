"""@package prep.py
Created on 11 June 2019

@author: castells
@description: Prepare the staging area. 

Define your staging main folder in settings.py 
When this is ran, it prepares a staging area with all the folders for each experiment. 
It also prepares the experiments.json file and places it in the default directory.

When it is ran again, only newly created experiment folders are added. 
Folders are not removed. 

If a new structure is needed, we may want to rebuild a  new staging area and rerun the programs

The staging area is a metadata folder with a folder per experiment.

This is for experiments only. 
I am not sure metdata is experiment.



"""


import json

import os
import stat
import sys 
import _connect


class Expt:
    """The class that will define an experiment and we can use that to make the folder. The row is the result of a query in the table
    
    
    """
    def __init__(self, row):      
        self.experiment_name = row.experiment_name
        self.KeyRefCode = row.KeyRefCode
        self.type = row.exptType 
        self.exptID = row.experiment_code 
        self.folder =  ''.join(ch for ch in row.experiment_code if ch.isalnum()).lower()
        self.station = self.folder[0]
        
    def asExptJson(self):
        '''
        "exptID": "rcs408",
        "Title": "Miscanthus sinensis giganteus study",
        "station": "r"
        '''
        expt =  {
              "Experiment": self.experiment_name,
              "KeyRefCode": self.KeyRefCode,
              "type": self.type,
              "exptID": self.folder,
              "expt_Code": self.exptID,
              "ExptFolder": self.folder,
              "Title": self.experiment_name,
              "station": self.station
            }        
        return expt
    
    '''
    def mkExptDir(self):
        status = " created"
        newDir = settings.STAGE+'metadata/'+self.exptID
        if not os.path.isdir(newDir):
            os.makedirs(newDir,  exist_ok = True)
            os.chmod(newDir, stat.S_IRWXO)
            status = " created"
        else: 
            os.chmod(newDir, stat.S_IRWXO)
            status = " here"
        return newDir + status
    '''

def getExperiments():
    """This gets the experiments. We only need experiments and farms
    
    SELECT Experiments.[Expt-Code], Experiments.Experiment, Experiments.KeyRefCode, Experiments.type, Experiments.[exp-ID]
    FROM Experiments
    WHERE ((Not (Experiments.type)="Other"))
    ORDER BY Experiments.Experiment;

    """
    cnx = _connect.connect()
    cur = cnx.cursor()

    sql = f'Select * from experiment where GLTENID > 0 order by experiment_name '
    cur.execute(sql)
    results = cur.fetchall() 

    presults = []
  
    for row in results:
        presults.append(row)
    return presults #a list of named tuples that behave like a list of objects. 

def makeJSON(results):
    expts =  []   
    for row in results: 
        ex = Expt(row)        
        expts.append(ex.asExptJson())  
    return expts

def makeIndexHtmlstr(newDir):
    '''idea to buid a specific html page to redirect people who are at the root of our directories to the actual experiment '''
    strIndex = 'copy index.html '+newDir+'\index.html'
    
    return strIndex 

def makeDir(newDir):
    '''checks the directory location exists and if it does not, creates it and prepares a strings that tell us what it did'''
    status = " created"
    if not os.path.isdir(newDir):
        os.makedirs(newDir,  exist_ok = True)
        os.chmod(newDir, stat.S_IRWXO)
        status = " created"
    else: 
        os.chmod(newDir, stat.S_IRWXO)
        status = " already here"
    return newDir + status




def makedirectories(results):  

    testString = ""
    default = "metadata/default/"
    stations = ["default", "rothamsted", "broomsbarn", "woburn", "saxmundham"]
    experiments =  [ "met", "rms", "bms", "wms", "sms", "rro", "rrn2"]
    

    
    for item in stations:
        defaultDir = stage+'metadata/'+item
        testString += makeDir(defaultDir) +'\n' 
    for item in experiments:
        exptDir = stage+'metadata/'+item
        testString += makeDir(exptDir) +'\n' 
        exptRepoDir = repo+'metadata/'+item
        testString += makeDir(exptRepoDir) +'\n' 
    
    for row in results: 
        ex = Expt(row)  
        exptDir = stage+'metadata/'+ex.folder
        testString += makeDir(exptDir) +'\n' 
        exptRepoDir = repo+'metadata/'+ex.folder
        testString += makeDir(exptRepoDir) +'\n'      
   
    return testString

def makeCopyString(results):  

    copyList = []
    default = "metadata\\default\\"
    stations = ["default", "rothamsted", "broomsbarn", "woburn", "saxmundham"]
    experiments =  [ "met", "rms", "bms", "wms", "sms", "rro", "rrn2"]
    

    
    for item in stations:
        defaultDir = 'metadata\\'+item
        copyList.append(makeIndexHtmlstr(defaultDir))
    for item in experiments:
        exptDir = 'metadata\\'+item
        copyList.append(makeIndexHtmlstr(exptDir)) 
        
        
    
    for row in results: 
        ex = Expt(row)  
        exptDir = 'metadata\\'+ex.folder
        copyList.append(makeIndexHtmlstr(exptDir))    
   
    return copyList



if __name__ == '__main__':
    #config = configparser.ConfigParser()
    #config.read('config.ini')
 

    stage = "d:/eRAWebStage/eRAstage27/" 
    repo = "d:/eRAWebRepo/repo07/"
    #stage = config['STAGE']['STAGE']
    #repo = config['STAGE']['REPO']
    status = " created"
    newDir = stage+'includes'
    defaultdir = stage+'metadata/default/'
    if not os.path.isdir(newDir):
        os.makedirs(newDir,  exist_ok = True)
        os.chmod(newDir, stat.S_IRWXO)
        status = " created"
    else: 
        os.chmod(newDir, stat.S_IRWXO)
        status = " already here"
    print (newDir + status)
    
    results = getExperiments()
    expts = makeJSON(results)
    strJsonExpts =  json.dumps(expts, indent=4)
    xname = stage+'metadata/default/experiments.json'    
    fxname = open(xname,'w+')
    fxname.write(strJsonExpts)
    fxname.close()
    print('Experiment file saved in '+xname)
    
    dirs = makedirectories(results)   
    copyStr = []
     
    print(strJsonExpts)
    print ("-----Directory Creation-----")
    print(dirs)
    
   
    
    #cpLs = makeCopyString(results)
    #for lines in cpLs:
        #print(lines)
