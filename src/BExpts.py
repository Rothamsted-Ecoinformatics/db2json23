'''
Created on 1 Oct 2019
This tests the fact that I can use _prep1 to interrogate GLTEN and return their json string

@author: castells

@TODO: colect the IDs that come from GLTN so that I can get the labels from there. 
'''
import pyodbc
import requests
import _connect
import settings
import json
import _images2json
#from pygments.lexers import sql
import _prep1


def prepareTOC(GLTENIDs):
    '''experiment_name = row.experiment_name,
            folder = row.experiment_code.replace('/','').lower(),
            GLTENID = row.GLTENID
            '''
    TOC = []
    for ID in GLTENIDs:
        TOC.append(dict(
            exptID= ID['folder'],
            Title= ID['experiment_name'],
            KeyRef = ID['KeyRef'],
            station = ID['folder'][0]                        
            ))
    return TOC

class Expt:
    """The class that will define an experiment and we can use that to make the folder. The row is the result of a query in the table
    
    
    """
    def __init__(self, row):      
        self.experiment_name = row.name
        self.KeyRefCode = row.key_ref_code
        self.exptID = row.code 
        self.folder =  ''.join(ch for ch in row.code if ch.isalnum()).lower()
        self.station = self.folder[0]
        self.keywords = "TEST - get keywords from the metadata"
        
    def asExptJson(self):
        '''
        "exptID": "rcs408",
        "Title": "Miscanthus sinensis giganteus study",
        "station": "r"
        '''
        
        expt =  {
              "Experiment": self.experiment_name,
              "KeyRefCode": self.KeyRefCode,
              "KeyRef": self.KeyRefCode,
              "exptID": self.folder,
              "expt_Code": self.exptID,
              "ExptFolder": self.folder,
              "Title": self.experiment_name,
              "station": self.station,
              "keywords": self.keywords
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

    sql = f'Select * from experiments where glten_id > 0 order by name '
    cur.execute(sql)
    results = cur.fetchall() 

    presults = []
    # Declaring namedtuple()   
    for row in results:
        presults.append(row)
    return presults #a list of named tuples that behave like a list of objects. 

def makeJSON(results):
    expts =  []   
    for row in results: 
        ex = Expt(row)        
        expts.append(ex.asExptJson())  
    return expts    


def process(exptID):
    
    
    data = _prep1.getData(exptID)
    
    if data != ' - ':
        for items in GLTENIDs:
            if items['GLTENID']== exptID:
                folder = items['folder']
      
        print(folder)
        # GLTENmetadata.json might be deprecated
        metadataJson =  json.dumps(data, indent=4)
        xname = settings.STAGE+ "metadata/"+str(folder)+"/GLTENmetadata.json"       
        fxname = open(xname,'w+')
        fxname.write(metadataJson)
        fxname.close()
        print("gltenmetadata.json saved in  = " + xname)
        
        
        
        
        experiment = _prep1.prepareExperiment(data) 
        experimentJson =  json.dumps(experiment, indent=4)
        xname = settings.STAGE+ "metadata/"+str(folder)+"/experiment.json"
        fxname = open(xname,'w+')
        fxname.write(experimentJson)
        fxname.close()
        print("experiment.json saved in  = " + xname)
        

          
        site = _prep1.prepareSite(data)
        siteJson =  json.dumps(site, indent=4)
        xname = settings.STAGE+ "metadata/"+str(folder)+"/site.json"
        fxname = open(xname,'w+')
        fxname.write(siteJson)
        fxname.close()
        print("site.json saved in  = " + xname)
        
           
        persons = dict (contributors = _prep1.preparePersons(data))
        personJson =  json.dumps(persons, indent=4)
        xname = settings.STAGE+ "metadata/"+str(folder)+"/person.json"
        fxname = open(xname,'w+')
        fxname.write(personJson)
        fxname.close()
        print("person.json saved in  = " + xname) 
        
        design = _prep1.prepareDesigns(data)
        designsJson = json.dumps(design, indent=4)
        xname = settings.STAGE+ "metadata/"+str(folder)+"/design.json"
        fxname = open(xname,'w+')
        fxname.write(designsJson)
        fxname.close()
        print("design.json saved in  = " + xname) 
        
        orgs = _prep1.prepareOrganization(data)
        orgsJson = json.dumps(orgs, indent=4)
        xname = settings.STAGE+ "metadata/"+str(folder)+"/orgs.json"
        fxname = open(xname,'w+')
        fxname.write(orgsJson)
        fxname.close()
        print("orgs.json saved in  = " + xname)
        
        # readme =_prep1.prepReadme(data)
        # xname = settings.STAGE+ "metadata/"+str(folder)+"/experiment.txt"
        # fxname = open(xname,'w+')
        # fxname.write(readme)
        # fxname.close()
        # print("experiment.txt saved in  = " + xname) 
        
        # mkdwn =_prep1.prepMD(data)
        # xname = settings.STAGE+ "markdownvault/experiment-"+str(folder)+".md"
        # fxname = open(xname,'w+')
        # fxname.write(mkdwn)
        # fxname.close()
        # print("markdown file saved in  = " + xname) 
         
        images = _images2json.getImages(folder)
        xname = settings.STAGE+"metadata/"+str(folder)+"/images.json"   
        fxname = open(xname,'w+')
        strJsimages =  json.dumps(images, indent=4)
        fxname.write(strJsimages)
        fxname.close()
        print('images.json saved in '+xname)
    else: 
        print('DATA NOT READY') 
 
if __name__ == '__main__':
    
  
    GLTENIDs = _prep1.getGLTENIDs()
    TOC = prepareTOC(GLTENIDs)
    TOCJson = json.dumps(TOC, indent=4)
    xname = settings.STAGE+ "metadata/default/experiments.json"
    fxname = open(xname,'w+')
    fxname.write(TOCJson)
    fxname.close()
    print("experiments.json saved in  = " + xname)
    
    results = getExperiments()
    expts = makeJSON(results)
    strJsonExpts =  json.dumps(expts, indent=4)
    xname = settings.STAGE+'metadata/default/experiments.json'    
    fxname = open(xname,'w+')
    fxname.write(strJsonExpts)
    fxname.close()
    print('Experiment file saved in '+xname)
    
    IDs = []
         
    for items in GLTENIDs:
        print (" %s (%s) GLTENID =  %s" % (items['experiment_name'],items['folder'], items['GLTENID']))
        exptID = items['GLTENID']
        print(exptID)
        process(exptID)
        print('\n')
    # we need to make the images for some folders which are not experiments
    #STATIONS = ["default", "rothamsted", "broomsbarn", "woburn", "saxmundham"]
#    EXPERIMENTS =  [ "met", "rms", "bms", "wms", "sms", "rro", "rrn2"]
    for station in settings.STATIONS:
        folder = station
        images = _images2json.getImages(folder)
        xname = settings.STAGE+"metadata/"+str(folder)+"/images.json"   
        fxname = open(xname,'w+')
        strJsimages =  json.dumps(images, indent=4)
        fxname.write(strJsimages)
        fxname.close()
    for extra in settings.EXPERIMENTS:
        folder = extra
        images = _images2json.getImages(folder)
        xname = settings.STAGE+"metadata/"+str(folder)+"/images.json"   
        fxname = open(xname,'w+')
        strJsimages =  json.dumps(images, indent=4)
        fxname.write(strJsimages)
        fxname.close()
        print('images.json saved in '+xname)
        
    allimages = _images2json.getAllImages()
    xname = settings.STAGE+"metadata/default/allimages.json"   
    fxname = open(xname,'w+')
    strJsimages =  json.dumps(allimages, indent=4)
    fxname.write(strJsimages)
    fxname.close()
    print('allimages.json saved in default')