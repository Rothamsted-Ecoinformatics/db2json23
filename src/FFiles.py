
"""@package csv2json
Created on 17/01/2021

@author: castells
@description: use this to convert the csv files like the bibliography, and the infofiles 
from csv to a json file of the same name. 

"""
import csv
import json
import settings


# Function to convert a CSV to JSON
# Takes the file paths as arguments
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
        
# Driver Code

# Decide the two file paths according to your
# computer system

if __name__ == '__main__': 
    
    
    toConvert = settings.toConvert
        
    for file in toConvert: 
    
        
        make_json(toConvert[file]['csvFilePath'], toConvert[file]['jsonFilePath'], toConvert[file]['idKey'])
        # Call the make_json function
        
    print("   ")   
    new_game = input(" All done - Hit return to close window")
    
           
    