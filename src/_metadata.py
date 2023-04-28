'''
Created on 9 Aug 2018

@author: ostlerr
@author: castells

ran on its own, it lists
This code lists the datasets in the database: you choose the one you want to process and it saves the Schema json in the relevant 
folder prepared in your staging area. See settings to set the staging area. 

This is used in CData to process the same thing for datasets and documents 

'''
import sys

import json

import settings
import AFolder
import _connect


class DocumentInfo:
    
    def __init__(self):
        """
tract 
        """
        self.url = None
        self.mdId = None
        self.data = {} # Changed declaration from NoneType to void non-subscriptable warnings
        self.folder = None
        self.sDOI = None

        
        
        
class Person:
    def __init__(self, row):
        self.familyName = row.family_name
        self.givenName = row.given_name 
        self.nameIdentifier = row.name_identifier 
        self.nameIdentifierScheme = row.name_identifier_scheme 
        self.schemeUri = row.scheme_uri 
        self.organisationName = row.name 
        self.street = row.street_address
        self.locality = row.address_locality 
        self.region = row.address_region 
        self.country = row.address_country 
        self.postalCode = row.postal_code
        self.fullname = self.givenName + " " + self.familyName
        if hasattr(row,'type_value'):
            self.contributorType = row.type_value
        self.nameIdentifiers = None
        if not self.nameIdentifier is None:
            self.nameIdentifiers = [
                {
                    "nameIdentifier": self.nameIdentifier,
                    "nameIdentifierScheme": self.nameIdentifierScheme,
                    "schemeURI": self.schemeUri 
                }
            ]
        self.affiliation = dict(type="Organization", name= self.organisationName,  address= self.formatAddress())
        
        
    def formatAddress(self):
        address = ""
        if not self.street is None:
            address = address + ", " + self.street
        if not self.locality is None:
            address = address + ", " + self.locality
        if not self.region is None:
            address = address + ", " + self.region
        if not self.postalCode is None:
            address = address + ", " + self.postalCode
        if not self.country is None:
            address = address + ", " + self.country
        return address
#        
    def asCreatorJson(self):
        dictaddress = dict(type="PostalAddress", streetAddress= self.organisationName, addressLocality= self.locality, addressRegion = self.region, postalCode= self.postalCode, addressCountry=self.country   )
        creator = dict(type = 'Person', Name = self.fullname,givenName = self.givenName,familyName = self.familyName, sameAs = self.nameIdentifier,address = dictaddress )
      
        creator["affiliation"] = self.affiliation
        return creator
    
    def asContributorJson(self):
        dictaddress = dict(type="PostalAddress", streetAddress= self.organisationName, addressLocality= self.locality, addressRegion = self.region, postalCode= self.postalCode, addressCountry=self.country   )
        contributor = dict(type = 'Person', jobTitle = self.contributorType, name = self.fullname, givenName = self.givenName, familyName = self.familyName, sameAs = self.nameIdentifier, address = dictaddress)
     
        contributor["affiliation"] = self.affiliation
        return contributor



def getDocumentMetadata(mdId):
    """ SELECT m.id as md_id, 
title, 
url,
identifier, 
identifier_type, 
dataset_type as dstype,
grt.type_value  as grt_value, 
srt.type_value  as dataset_type,  
srt.type_value  as srt_value,
document_format_id,
e.field_id,
f.name as fieldname,
f.geo_point_latitude, 
f.geo_point_longitude, 
e.name as experiment_name, 
e.code  as experiment_code,
publication_year,
short_name,
publisher_id, 
is_ready,
o.name as publisher, 
version, 
lang,  
grade, 
is_external,
description_abstract,
description_methods,
description_toc,
description_technical_info,
description_quality,
description_provenance,
description_other,
doi_created,
document_format_id as extension, 
rights_text, 
rights_licence_uri, 
rights_licence
FROM metadata_documents m
join experiments e on m.experiment_id = e.id 
join fields f on e.field_id = f.id 
join organisations o on o.id = m.publisher_id
join general_resource_types grt on grt.id = m.general_resource_type_id 
join specific_resource_types srt on srt.id = m.specific_resource_type_id ;
encapsulted in a view
    
    
    
    
    """
    
    cnx = _connect.connect()
    cur = cnx.cursor()
    
    cur.execute("""select * from vw_metadata_documents  where md_id = ? order by grade DESC, title ASC""", mdId)
    return cur

# def prepareCreators_new(mdId):
#     cnx = _connect.connect()
#     cur = cnx.cursor()
#     creators = ""
#     # First prepare named people
#     cur.execute('select p.family_name, p.given_name, p.name_identifier, p.name_identifier_scheme, p.scheme_uri, o.organisation_name, o.street_address, o.address_locality, o.address_region, o.address_country, o.postal_code from (person p inner join person_creator pc on p.person_id = pc.person_id) inner join organisation o on p.affiliation = o.organisation_id where pc.md_id = ?', mdId)
#     
#     results = cur.fetchall()    
#     for row in results: 
#         person = Person(row)  
#      
#         creators.append(person.asCreatorJson())
#            
#     # second prepare organisations
#     cur.execute('select * from organisation o inner join organisation_creator oc on o.organisation_id = oc.organisation_id where oc.md_id = ?',mdId)
#     results = cur.fetchall()
#     for row in results:
#      
#         creators.append({"creatorName": row.organisation_name}) 
#         
#     return creators 
   
def prepareCreators(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    creators = []
    # First prepare named people
    # corrected for 2023
    cur.execute('select p.family_name, p.given_name, p.name_identifier, p.name_identifier_scheme, p.scheme_uri, o.name, o.street_address, o.address_locality, o.address_region, o.address_country, o.postal_code from (persons p inner join person_creators pc on p.id = pc.person_id) inner join organisations o on p.organisation_id = o.id where pc.metadata_document_id  = ?', mdId)
    
    results = cur.fetchall()    
    for row in results: 
        person = Person(row)  
     
        creators.append(person.asCreatorJson())
           
    # second prepare organisations
     # corrected for 2023
    cur.execute('select * from organisations o inner join organisation_creators oc on o.id = oc.organisation_id where oc.metadata_document_id  = 70 ?',mdId)
    results = cur.fetchall()
    for row in results:
     
        creators.append({"type": "organization", "name": row.name}) 
        
    return creators

def prepareContributors(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    contributors = [] 
    # First prepare named people
    cur.execute("""select p.family_name, p.given_name, p.name_identifier, p.name_identifier_scheme, p.scheme_uri, o.organisation_name, o.street_address, o.address_locality, o.address_region, o.address_country, o.postal_code, prt.type_value 
        from ((person p 
        inner join organisation o on p.affiliation = o.organisation_id) 
        inner join person_role pr on p.person_id = pr.person_id)
        inner join person_role_types prt on pr.prt_id = prt.prt_id
        where pr.md_id = ?""", mdId)
    
    results = cur.fetchall()    
    for row in results: 
        person = Person(row)        
        contributors.append(person.asContributorJson())
    # second prepare organisations
    cur.execute("""select o.organisation_name, ort.type_value 
        from (organisation o 
        inner join organisation_role r on o.organisation_id = r.organisation_id) 
        inner join organisation_role_types ort on r.ort_id = ort.ort_id
        where r.md_id = ?""",mdId)
    results = cur.fetchall()
    for row in results:
        contributors.append({"sourceOrganisation": row.organisation_name}) 
        
    return contributors    
    
def prepareSubjects(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    subjects = []
    cur.execute("""select s.subject, s.subject_uri, ss.subject_schema, ss.schema_uri
        from (subjects s
        inner join subject_schemas ss on s.ss_id = ss.ss_id)
        inner join document_subjects ds on s.subject_id = ds.subject_id 
        where ds.md_id = ?""", mdId)
    results = cur.fetchall()    
    for row in results: 
        subjects.append(row.subject)
        
    return subjects
    
def prepareDescriptions(row):
    descriptions = []
    
    descriptions.append({'inLanguage' : row.language, 'descriptionType' : 'Abstract', 'description' : row.description_abstract})
    if not row.description_methods is None:
        descriptions.append({'inLanguage' : row.language, 'descriptionType' : 'Methods', 'description' : row.description_methods})
    if not row.description_toc is None:
        descriptions.append({'inLanguage' : row.language, 'descriptionType' : 'TableOfContents', 'description' : row.description_toc})
    if not row.description_technical_info is None:
        descriptions.append({'inLanguage' : row.language, 'descriptionType' : 'TechnicalInfo', 'description' : row.description_technical_info})
    if not row.description_other is None:
        descriptions.append({'inLanguage' : row.language, 'descriptionType' : 'Other', 'description' : str(row.description_other)})
    if not row.description_provenance is None :
        descriptions.append({'inLanguage' : row.language, 'descriptionType' : 'Provenance', 'description' : str(row.description_provenance) })
    if not row.description_quality is None :
        descriptions.append({'inLanguage' : row.language, 'descriptionType' : 'Quality', 'description' :  str(row.description_quality) })

    return descriptions

def prepareDateCreated(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    cur.execute("""select dt.type_value, dd.document_date from document_dates dd inner join date_types dt on dd.dt_id = dt.dt_id where dd.md_id = ?""", mdId)
    
    results = cur.fetchall()    
    for row in results: 
        if row.type_value == 'Created':
            return row.document_date.strftime('%Y-%m-%d')  

def prepareDateAvailable(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    cur.execute("""select dt.type_value, dd.document_date from document_dates dd inner join date_types dt on dd.dt_id = dt.dt_id where dd.md_id = ?""", mdId)
    
    results = cur.fetchall()    
    for row in results: 
        if row.type_value in ('Available', 'Accepted') :
            return row.document_date.strftime('%Y-%m-%d')  


def prepareDateModified(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    cur.execute("""select dt.type_value, dd.document_date from document_dates dd inner join date_types dt on dd.dt_id = dt.dt_id where dd.md_id = ?""", mdId)
    
    results = cur.fetchall()    
    for row in results: 
        if row.type_value == 'Updated' :
            return row.document_date.strftime('%Y-%m-%d')  
        
def getInfo(database_identifier):
    '''This function looks for a URL or DOI in the document table and returns its title if it is there'''
    cnx = _connect.connect()
    cur = cnx.cursor()
    sqldi = "select title, grt_value  from vw_metadata_documents where identifier = '{}'" 
    #print(sqldi.format(database_identifier))
    #cur.execute("""select title, grt_value  from vw_metadata_documents where identifier =  ?""", database_identifier)
    cur.execute(sqldi.format(database_identifier))
    
    result_row = cur.fetchone()
    if result_row:
        # there was a result
        return {'title':result_row.title, 'grt_value':result_row.grt_value}
    else:
        return {'title':'NONE', 'grt_value':'Text'}
    
   

def prepareRelatedIdentifiers(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    related_identifiers = []
    cur.execute("""select ri.related_identifier, ri.ri_name as ri_name, i.type_value as identifier_type, r.rt_desc as type_description, ri.rt_id as rtID, r.type_value as relation_type
        from (related_identifiers ri
        inner join identifier_types i on ri.it_id = i.it_id)
        inner join relation_types r on ri.rt_id = r.rt_id
        where ri.md_id = ?""", mdId)
    
    results = cur.fetchall() 
    ri_name_v = ''
    ri_type_v = 'Text'  
    for row in results: 
        
        RI_info = getInfo(row.related_identifier)
        if RI_info['title'] != 'NONE':
            ri_name_v =  RI_info['title']
            ri_type_v = RI_info['grt_value']
        else:
            ri_name_v =  row.ri_name
            ri_type_v = 'Text'
            
    
         
       
        related_identifiers.append({
            'relatedIdentifier': row.related_identifier,
            'relatedIdentifierType' : row.identifier_type, 
            'name': ri_name_v,
            'relatedIdentifierGeneralType': ri_type_v,
            'relationType' : row.relation_type, 
            'rt_id': row.rtID, 
            'relationTypeValue': row.type_description
            })
        
    return related_identifiers    

def prepareSizes(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    sizes = []
    cur.execute("""select u.unit_short_name, ds.size_value
        from document_sizes ds inner join measurement_unit u on ds.unit_id = u.unit_id where ds.md_id = ?""", mdId)
    
    results = cur.fetchall()    
    for row in results: 
        if row.unit_short_name == 'None':
            sizes.append(row.size_value)
        else:
            sizes.append(str(row.size_value) + ' ' + row.unit_short_name)
        
    return sizes

def prepareFundingReferences(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    fundingreferences = []
    cur.execute("""select fa.award_number, fa.award_uri, fa.award_title,fb.organisation_name, fb.funder_identifier, fb.funder_identifier_type
        from (document_funding df
        inner join funding_awards fa on df.fa_id = fa.fa_id)
        inner join organisation fb on fa.organisation_id = fb.organisation_id
        where df.md_id = ?""", mdId)

    results = cur.fetchall()
    for row in results:
        fundingreferences.append(
           {
               "type": "organization",
               "name": row.organisation_name,
               "sameAs": row.funder_identifier,
               "award":  row.award_number + ' - ' + row.award_title,
               "identifier": row.award_uri
            }
        )
        
    return fundingreferences

def prepareDistribution(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    distribution = []
    
    rows_count = cur.execute("""SELECT ds_id, md_id, unit_short_name, size_value, location, file_name         
        FROM document_sizes ds left join measurement_unit as mu on ds.unit_id = mu.unit_id
        where isIllustration = 0 and ds.md_id = ?""", mdId)

    try:
        results = cur.fetchall()
        for row in results:
            
            fileName = row.location
            if fileName:
                fileParts = fileName.split(".")
                encodingFormat = fileParts[-1]
                distribution.append(
                {
                    "type": "dataDownload",
                    "name": row.file_name,
                    "URL": fileName,
                    "encodingFormat":  encodingFormat,
                    "fileSize": str(row.size_value) + ' ' + row.unit_short_name
                }
                )  
            else:
                encodingFormat = ''
            
    except TypeError:
        distribution = []
    return distribution

def prepareIllustration(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    illustration = []
    
    rows_count = cur.execute("""SELECT ds_id, md_id, unit_short_name, size_value, location, file_name         
        FROM document_sizes ds left join measurement_unit as mu on ds.unit_id = mu.unit_id
        where isIllustration = 1 and ds.md_id = ?""", mdId)

    try:
        results = cur.fetchall()
        for row in results:
            
            fileName = row.location
            if fileName:
                fileParts = fileName.split(".")
                encodingFormat = fileParts[-1]
            else:
                encodingFormat = ''
            illustration.append(
                {
                    "type": "imageObject",
                    "caption": row.file_name,
                    "URL": fileName,
                    "encodingFormat":  encodingFormat,
                    "fileSize": str(row.size_value) + ' ' + row.unit_short_name
                }
                )  
    except TypeError:
        illustration = []
    return illustration

def process(documentInfo):
    mdId = documentInfo.mdId
    mdCursor = getDocumentMetadata(mdId)
    mdRow = mdCursor.fetchone()
    data = None
    #print("Dataset ID is: " + mdId)
    if mdRow:
        mdUrl = mdRow.url
        documentInfo.url = mdUrl        
        #print(documentInfo.url)
        mdExpt =  mdRow.experiment_code
        documentInfo.expt = mdExpt
        #print(documentInfo.expt)
        folder = ''.join(ch for ch in mdExpt if ch.isalnum()).lower()
        documentInfo.folder = folder
        #print(folder)
        sDOI = mdRow.identifier[9::]
        documentInfo.sDOI = sDOI
        documentInfo.shortName = mdRow.short_name
        documentInfo.version = str(mdRow.version)
        #print(sDOI)
      
        data = {
            '@context' : 'https://schema.org/',
            '@type' : mdRow.grt_value,           
            'identifier' : mdRow.identifier,
            'name' : mdRow.title.strip(),
            'shortName':mdRow.short_name.strip() if mdRow.short_name else '',
            'url': mdRow.url,
            'description': prepareDescriptions(mdRow),
            'publisher' :{
                "type": "organization",
                "name": mdRow.publisher
                },
            'publication_year' : mdRow.publication_year,
            'dateCreated' : prepareDateCreated(mdId),
            'dateModified' : prepareDateModified(mdId),
            'datePublished' : prepareDateAvailable(mdId),
            'inLanguage' : mdRow.language,  
            'version' : str(mdRow.version), 
            'keywords' : prepareSubjects(mdId),
            'creator' : prepareCreators(mdId),
            'contributor' : prepareContributors(mdId),
            'encodingFormat' : mdRow.mime_type,
            'copyrightHolder' : {
                "type": "organization",
                "name": mdRow.publisher
                },
            'license':  {
                "type": "CreativeWork",
                "name": "Attribution 4.0 International (CC BY 4.0)",
                "license": mdRow.rights_licence_uri,
                "text": mdRow.rights_licence
                },
            'spatialCoverage': 
                {
                    'type': 'place',
                    'geo' : {
                        'type':'GeoCoordinates',
                        'longitude': float(mdRow.geo_point_longitude),
                        'latitude': float(mdRow.geo_point_latitude)
                    },
                    'name': mdRow.fieldname            
                },
            'relatedIdentifier': prepareRelatedIdentifiers(mdId),
            'funder' : prepareFundingReferences(mdId),
            'distribution' : prepareDistribution(mdId),
            'image' : prepareIllustration(mdId),
            'grade': mdRow.grade if mdRow.grade   else 1,
            'isExternal': mdRow.isExternal if mdRow.isExternal else 0,
            'dstype': mdRow.dstype if mdRow.dstype else 'N/A'
        }
        ##print(data)
        
    documentInfo.data = data    
    return documentInfo    

def save(documentInfo): 
  
    if documentInfo.data['@type'][0].lower() == "t":
        datasetFolder = str(documentInfo.folder)
    else: 
        datasetFolder = str(documentInfo.folder)+"/"+ str(documentInfo.shortName)
    dirname =  settings.STAGE+ "metadata/"+datasetFolder
    AFolder.makeDir(dirname)
    repoName =  settings.REPO+ "metadata/"+datasetFolder
    AFolder.makeDir(repoName)
    strVersion = ""
    if documentInfo.version is None:
        strVersion = "01"
    else: 
        if int(documentInfo.version) <10: 
            strVersion = "0"+str(documentInfo.version).lstrip('0')
        else:
            strVersion = str(documentInfo.version) 
    xname = dirname +"/"+ strVersion + "-" + str(documentInfo.shortName) +".json"
    #print (xname)
    fxname = open(xname,'w+')
    strJsDoc =  json.dumps(documentInfo.data, indent=4)
    #print (strJsDoc)
    fxname.write(strJsDoc)
    fxname.close()
   
    #print('json document saved in '+ xname)
    
    
def getDOCIDs():
    #list 
    DOCIDs = []
    cnx = _connect.connect()
    cur = cnx.cursor()
    cur.execute("""select * from vw_metadata_documents where grt_value like 'dataset' order by 'URL'  """)
    results = cur.fetchall()  
    counter = 0  
    for row in results: 
        
        counter +=1  
        DOCIDs.append(dict(
            nb = counter,
            documentID = row.md_id,
            title = row.title.strip(),
            expCode = row.experiment_code))
           
        
    return DOCIDs 

def get_document_json(dataset_id):
    documentInfo = DocumentInfo()  
    documentInfo.mdId = dataset_id
    documentInfo = process(documentInfo)
    ##print(json.dumps(documentInfo.data, indent=4))
    return documentInfo.data

def makeDocumentInfo(dataset_id):
    documentInfo = DocumentInfo()  
    documentInfo.mdId = dataset_id
    documentInfo = process(documentInfo)
    save(documentInfo)
    
if __name__ == '__main__':
    try:
        #-28178770 is a dataset
        #-1140916605 has author
        # 4 is a text 
    
        
        while True:
            datasetID = 0
             
            DOCIDs = getDOCIDs()
       
            IDs = []     
            tokens = []
            counter = 0
            for items in DOCIDs: 
                counter = counter + 1
                #print ("%s -  %s (%s) DOCIDs =  %s" % (counter, items['title'],items['expCode'], items['documentID']))
                IDs.append(str(items['documentID']))
                tokens.append(str(counter))
            #print (" ")  
            #print(tokens)
        
            token = '0'
            while token == '0':
                token = input('Which dataset? ')
                #print(token)
                if token  not in tokens:
                    #print("not in the list")
                    token = '0'
                else: 
                    inToken = int(token)
                    inToken = inToken - 1
                    datasetID = IDs[inToken]
                #print (datasetID)
            
            makeDocumentInfo(datasetID)
            
           
            new_game = input("Would you like to do another one? Enter 'y' or 'n' ")
            if new_game[0].lower()=='y':
                playing=True
                continue
            else:
                #print("Thanks for your work!")
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
    

