"""@package indexDatasets.py
Created on 6 july 2021

@author: castells
@description: this tool
 
- Gets all the datasets
- concatenates all the texts from the datasets, 
- list the unique words in a list except for the ones in an exclusion list


"""
import sys
import pyodbc
import json
import settings
import _connect


def getDatasets_words():
    ''' this does not work.. infuriating
    I am trying to make a list of the datasets with a list of words attached'''
    
    datasetsWords = []
    cnx = _connect.connect()
    cur = cnx.cursor()
    sql = 'select identifier,  title, description_abstract, description_methods, description_toc, description_technical_info, description_quality , description_provenance, description_other  from viewMetaDocument where grt_value like \'Dataset\' '
    cur.execute(sql)
    results = cur.fetchall()
    stralph = 'abcdefghijklmnopqrstuvwxyz'
    auth_list = [it for it in stralph]
    auth_list.append(['-', '.'])     
    
    for row in results: 
        ''' concatenate all the fields in one'''
        rowText = '{} {} {} {} '.format(row.title, row.description_abstract, row.description_methods, row.description_technical_info)         
        rowList = rowText.split()
        dsWords = []
        for word in rowList:
            word = ''.join(i for i in word.lower() if i in auth_list).lower()
            if word not in dsWords:
                dsWords.append(word)
                dsWords.sort()
        print(rowDataset)       
        print(dsWords)      
        datasetsWords.append(dict(
            dataset=row.identifier, 
            keywords=dsWords)
        )  
    return dwords


def getWords():
    words = []
    cnx = _connect.connect()
    cur = cnx.cursor()
    sql = 'select identifier,  title, description_abstract, description_methods, description_toc, description_technical_info, description_quality , description_provenance, description_other  from viewMetaDocument where grt_value like \'Dataset\' '
    cur.execute(sql)
    results = cur.fetchall()
    stralph = 'abcdefghijklmnopqrstuvwxyz'
    auth_list = [it for it in stralph]
    auth_list.append(['-', '.']) 
    
    for row in results: 
        ''' concatenate all the fields in one'''
        rowDataset = row.identifier
        rowText = '{} {} {} {} '.format(row.title, row.description_abstract, row.description_methods, row.description_technical_info)         
        rowList = rowText.split()
        for word in rowList:
            word = ''.join(i for i in word.lower() if i in auth_list).lower()
            if word not in words:
                words.append(word.lower())
                words.sort()
        
    return words 


if __name__ == '__main__':
    try:   
        words = getWords()
        counter = 0
        for word in words:
            counter += 1
            print ('{} = {}'.format(counter, word))
        
    except:
        print('Error')
    
    
