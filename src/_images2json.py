"""@package image2json
Created on 11 June 2019

@author: castells
@description: Use this tool to export the images for the experiments. 

How to use: just run this app, and copy the resulting file in the metadata/default folder. 
As the ExptID is with each image, there is no need to have one file per experiment. 


"""

import pyodbc
import json
import _connect
import settings

# def connect():
#     """Function to connect to the datasource"""
#     conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\castells\Rothamsted Research\e-RA - Documents\General\website development\accessTools\timeline.accdb;')    
#     return conn

# def getCursor():
#     """Returns a new Cursor object using the connection"""
#     con = connect()
#     cur = con.cursor()
#     return cur


class Image:
    """The class that will define an image. The row is the result of a query in the table
    try remove "settings.ROOT+" from URL 
    #
    SELECT i.id,  
i.is_reviewed , 
i.file_location , 
i.is_www , 
i.person_id , 
p.given_name, 
p.family_name, 
i.caption, 
i.description, 
i.height, 
i.width, 
i.orientation, 
i.experiment_code
FROM images i
JOIN persons p on i.person_id = p.id  


    """
    def __init__(self, row):
        self.MediaID = row.id 
        self.Credit = row.given_name+" "+row.family_name 
        self.URL = "images/"+row.file_location  
        self.Caption = row.caption 
        self.Type = row.image_type 
        self.exptID = row.experiment_code 
        self.isReviewed = row.is_reviewed 
        self.forWWW = row.is_www
        self.width = row.width 
        self.height = row.height 
        self.orientation = row.orientation 
        self.fileLocation = row.file_location 
        
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
    cnx = _connect.connect()
    cur = cnx.cursor()
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


    sql = f"SELECT i.id,  i.is_reviewed , i.file_location , i.is_www , i.person_id , p.given_name, p.family_name, i.caption, i.description, i.height, i.width, i.orientation, i.experiment_code, i.image_type FROM images i JOIN persons p on i.person_id = p.id where  experiment_code like \'{exptID}\' "
    #sql = f"Select * from qsMediasWWW where  exptID like \'{exptID}\' "
    # print(sql)
    cur.execute(sql)
    results = cur.fetchall()  
    for row in results: 
        im = Image(row)        
        images.append(im.asImageJson())  
    return images


def getAllImages():
    cnx = _connect.connect()
    cur = cnx.cursor()
    images = []
    
#
#name = 'Tushar'
#age = 23
#print(f"Hello, My name is {name} and I'm {age} years old.")

    # cur.execute("""select * from viewMetaDocument  where md_id = ? order by grade DESC, title ASC""", mdId)
    


    #sql = f"Select * from qsMediasWWW "
    sql = f"SELECT i.id,  i.is_reviewed , i.file_location , i.is_www , i.person_id , p.given_name, p.family_name, i.caption, i.description, i.height, i.width, i.orientation, i.experiment_code, i.image_type FROM images i JOIN persons p on i.person_id = p.id"
    # print(sql)
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
    
    