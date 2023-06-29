"""@package settings.py
Created on 13 june 2019

@author: castells
@description: general settings of the web site

ROOT: URL for the web site
STAGE: where all the files are going to be dumped. 
DEFAULT: name of the default folder for jsons files releant to whole site. Do not change

STATIONS: List of stations (until that is handled by the database)
EXPERIMENTS: list experiment that need a folder but have no GLTENID
"""

#import configparser 

#config = configparser.ConfigParser()
##config.read('config.ini')
#ROOT    = config['STAGE']['ROOT']
#STAGE   = config['STAGE']['STAGE'] 
#REPO    = config['STAGE']['REPO']


STAGE = "d:/eRAWebStage/eraGilbert01/" 
REPO = "d:/eRAWebRepo/repo08/"
ROOT = "http://local-info.rothamsted.ac.uk/eRA/era2023/"
INTRA = 'P://era2023/'

DEFAULT = "metadata/default/"
IMAGES = "images/metadata"
STATIONS = ["default", "rothamsted", "broomsbarn", "woburn", "saxmundham"]
EXPERIMENTS =  [ "met", "rms", "bms", "wms", "sms", "rro", "rrn2"]
DEFAULTDIR = STAGE+DEFAULT

toConvert = {
                'infofiles' : {
                    'csvFilePath': INTRA+DEFAULT+'infofiles.csv',
                    'jsonFilePath': DEFAULTDIR+'infofiles.json',
                    'idKey' : 'id'
                        }
                #'papers' : {
                #    'csvFilePath': INTRA+DEFAULT+'papers.csv',
                 #   'jsonFilePath': DEFAULTDIR+'papers.json',
                #    'idKey' : 'PaperID'
                #        }
                #
                }

def bye(): 
    print("   ")
    print("Thanks for your work!")
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


if __name__ == '__main__':
    print('ROOT: {}'.format(ROOT))
    print('STAGE: {}'.format(STAGE))
    print('REPO: {}'.format(REPO))