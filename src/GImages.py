"""@package 

TODO: i need to create a list of the ones that are ready to save. or pop out the items in the ready to save 
that are not renamed. Then only kjeep the ready to save until the author has renamed or I redo the renaming anyway! !

"""


import pyodbc
import json
import _connect
import settings
import os
import _images2json
from PIL import Image




def getStored():
    # 2: Make a list of the file Locations of images stored on the INTRANET drive (metadata) 
    imStored = []
    avoid = ['.xls', '.txt', '.AVI', '.mp4', 'docx', '.csv']
    # readDir = 'P:/era2023/images/metadata/'
    readDir = settings.INTRA+settings.IMAGES
    for path, directories, files in os.walk(readDir):
        for file in files:
            passed = 'yes'
            if any(x in file for x in avoid): 
                passed = 'no'
            if passed == 'yes':
                imStored.append(path.replace('\\','/').replace('P://era2023/images/','') +'/'+ file)
    return imStored 
                       
                
def getFiles(): 
    # 1: Make a list of the filelocations of images stored in the database
    images = _images2json.getAllImages()
    imLoc = []
    for image in images:
        imLoc.append( image['fileLocation'])      
    return imLoc

def getProperties(image):
    
    # we get the file name, extract the caption from the file name the image dimensions, 
    # the experiment code from the path, and so on"""
    print(image)
    folder =  'P:/era2023/images/'
    imagefile = os.path.join(folder,  image)
    img = Image.open(imagefile)
    width = img.width
    height = img.height
    orientation = 'lanscape'
    if width < height:
        orientation='portrait'
    filename = image.split('/')[-1]
    expCode = image.split('/')[-2]
    caption = filename.replace('-', ' ').split('.')[-2]
    properties = dict(
        file_location =image,
        person_id=71,
        width = width,
        height = height,
        orientation = orientation,
        organisation_id = 1,
        is_www = 0,
        is_reviewed = 0,
        image_type_id = 1,
        image_type = 'metadata',
        filename = filename,
        experiment_id = 1,
        experiment_code = expCode,
        description = "Space for a longer caption",
        caption = caption
    )
    return properties
 
def makeCSV(file):
    '''Prepare a function to make a CSV file to import in the database'''
    pass

def rename(tosave):
    '''prepare a function to rename a file
    TODO: get the actual original file name, create the new one, and rename 
    '''
    removed = []
    
    exList = [' ', '_', '&', ',']
    for nb in range(len(tosave)):
        old_file = tosave[nb]
        new_file = tosave[nb]
        if any(x in old_file for x in exList): 
            for x in exList:
                new_file = new_file.replace(x,'-').replace('--','-')
            oldfile =  old_file.replace('/','\\')
            newfile =  new_file.replace('/','\\')
            removed.append(" {} needs  renaming  to  {}".format(oldfile, newfile))
        else:
            pass
    # old_file = os.path.join("D:\dump", oldfile)
    # new_file = os.path.join("D:\dump", newfile)
    # os.rename(old_file, new_file)
    return removed
   
def importImage(file):
    propFile = getProperties(file);
    try:
        con = _connect.connect()
        cur = con.cursor()
        prepStatement = '''INSERT INTO images (file_location,  person_id,  caption,  image_type,  description, 
                width,  height, orientation,  experiment_code,  is_www,  is_reviewed, 
                filename,  organisation_id,   image_type_id)
                VALUES(
                    '{file_location}',   71,  '{caption}',  'metadata',  '{description}', 
                {width},  {height},   '{orientation}',  '{experiment_code}',  0,  0, 
                '{filename}', 1,  1)
                '''.format(
                    file_location = propFile['file_location'],
                    caption = propFile['caption'],
                    description = propFile['description'],
                    width = propFile['width'],
                    height = propFile['height'],
                    orientation = propFile['orientation'],
                    experiment_code = propFile['experiment_code'],
                    filename = propFile['filename']
                    
                    )
        # print(prepStatement)
        cur.execute(prepStatement);

        con.commit()
    except AttributeError as error:
        print(error)
    except pyodbc.Error as error:
        print(error)



if __name__ == '__main__':
    # 1: Make a list of the filelocations of images stored in the database
    
    dbLoc = getFiles()
    print ("---- {} images in the database eraGilbert --------------".format(len(dbLoc)))
    print ("\n\n ")
    
    # 2: Make a list of the file Locations of images stored on the INTRANET drive (metadata) 
    stLoc = getStored()
    for loc in stLoc: 
        print(loc)
    
    play = input ("---- {} images in the INTRANET drive --------------".format(len(stLoc)))

    
    
    tosave = []
    for loc in stLoc:
        
        if loc not in dbLoc:
            
            tosave.append(loc)
        
            print(loc + ' not found in the database')
        else: 
            print(loc + ' here')
    suite = input("------- Let's see if there is some renaming to do!  ")     
    removed = rename(tosave)
    
    # 3: finding what is in database but not in files
    
    missing= []
    for loc in dbLoc: 
        if loc not in stLoc:
            missing.append(loc)
            print(loc + ' not found in the drive')
    
           
    print ("---- {} images in to import --------------".format(len(tosave))) 
    print (" ")
    

    
    
    for logline in removed:
        print(logline)
        
    print (" ")
    print (" ")
    print ("---- {} images in to rename -----".format(len(removed)))
     
    print (" ")
    print (" ")
    print ("---- These  {} images can be saved now ------".format(len(tosave)))
    
    for logline in tosave:
        print(logline)
    print (" ")
    print (" ")   
    new_game = input("Would you like to save them ? Enter 'y' or 'n' ")
    if new_game[0].lower()=='y':
        for image in tosave:        
            importImage(image)
    else: 
        
        finish = input("Thanks for your work:) ")
        pass
    print (" ")
    print (" ")
    print ("     .-******-. ")
    print ("   .'          '. ")
    print ("  /   O      O   \ ")
    print (" :                : ")
    print (" |                | ")
    print (" : ',          ,' : ")
    print ("  \  '-......-'  / ")
    print ("   '.          .' ")
    print ("     '-......-' ")
    