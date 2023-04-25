"""@package image2json
Created on 11 June 2019

@author: castells
@description: Use this tool to export the images for the experiments. 

How to use: just run this app, and copy the resulting file in the metadata/default folder. 
As the ExptID is with each image, there is no need to have one file per experiment. 


"""

import pyodbc
import json
import settings

def connect():
    """Function to connect to the datasource"""
    conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\castells\Rothamsted Research\e-RA - Documents\General\website development\accessTools\timeline.accdb;')    
    return conn

def getCursor():
    """Returns a new Cursor object using the connection"""
    con = connect()
    cur = con.cursor()
    return cur


class Image:
    """The class that will define an image. The row is the result of a query in the table
    try remove "settings.ROOT+" from URL 
    """
    def __init__(self, row):
        self.MediaID = row.mediaID 
        self.Credit = row.Credit 
        self.URL = "images/"+row.fileLocation  
        self.Caption = row.Caption 
        self.Type = row.Type 
        self.exptID = row.exptID 
        self.isReviewed = row.isReviewed 
        self.forWWW = row.forWWW
        self.width = row.width 
        self.height = row.height 
        self.orientation = row.orientation 
        self.fileLocation = row.fileLocation 
        
    def asImageJson(self):    
        image =  {         
              "MediaID": self.MediaID,
              "Credit": self.Credit,
              "URL": self.URL,
              "Caption": self.Caption,
              "Type":   self.Type,
              "exptID": self.exptID,
              "width": self.width,
              "height": self.height,
              "orientation": self.orientation,
              "fileLocation": self.fileLocation,
              "isWWW":  self.forWWW,
              "isReviewed":  self.isReviewed,
                     
            }        
        return image


def getImages(exptID = 'rothamsted'):
    cur = getCursor()
    images = []
    
#
#name = 'Tushar'
#age = 23
#print(f"Hello, My name is {name} and I'm {age} years old.")

    # cur.execute("""select * from viewMetaDocument  where md_id = ? order by grade DESC, title ASC""", mdId)
    #  
#  SELECT Media.mediaID, Media.URL, Media.isReviewed, Media.fileLocation, "http://local-info.rothamsted.ac.uk/eRA/era2018-new/images/" & [fileLocation] AS cURL, Media.forWWW, Media.Credit, Media.Caption, Media.Type, Media.Description, Media.height, Media.width, Media.orientation, Media.exptID
#  FROM Media
#  WHERE (((Media.forWWW)=True) AND ((Media.Type) Like "Other"))
#  ORDER BY Media.fileLocation, "http://local-info.rothamsted.ac.uk/eRA/era2018-new/images/" & [fileLocation], Media.exptID;

# this selects the ones who are selected for for WWW which is the galleries. 



    sql = f"Select * from qsMediasWWW where  exptID like \'{exptID}\' "
    print(sql)
    cur.execute(sql)
    results = cur.fetchall()  
    for row in results: 
        im = Image(row)        
        images.append(im.asImageJson())  
    return images


def getAllImages():
    cur = getCursor()
    images = []
    
#
#name = 'Tushar'
#age = 23
#print(f"Hello, My name is {name} and I'm {age} years old.")

    # cur.execute("""select * from viewMetaDocument  where md_id = ? order by grade DESC, title ASC""", mdId)
    


    #sql = f"Select * from qsMediasWWW "
    sql = f"Select * from Media "
    print(sql)
    cur.execute(sql)
    results = cur.fetchall()  
    for row in results: 
        im = Image(row)        
        images.append(im.asImageJson())  
    return images
    

if __name__ == '__main__':
  
    exptID = 'rbk1'

    images = getImages(exptID)
    xname = settings.STAGE+"metadata/"+exptID+"/images.json"   
    fxname = open(xname,'w+')
    strJsimages =  json.dumps(images, indent=4)
    print (strJsimages)
    fxname.write(strJsimages)
    fxname.close()
    print('Images.json saved in '+xname)
    
    