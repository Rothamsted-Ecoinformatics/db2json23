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
    #print("debug _metadata ln 24: doing DocumentInfo")
    def __init__(self):
        
        self.url = None
        self.mdId = None
        self.data = {} # Changed declaration from NoneType to void non-subscriptable warnings
        self.folder = None
        self.sDOI = None

 
        
class Person:
    
    # checked for eraSandpit: 2023-04-28
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
            #print("debug _metadata ln 53 - Person")
            #print(row.type_value)
        self.nameIdentifiers = None
        if not self.nameIdentifier is None:
            self.nameIdentifiers = [
                {
                    "nameIdentifier": self.nameIdentifier,
                    "nameIdentifierScheme": self.nameIdentifierScheme,
                    "schemeURI": self.schemeUri 
                }
            ]
        #print("debug _metadata ln 64 - Person")
        #print(self.nameIdentifiers)
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
        #print("debug _metadata ln 81 - Person")
        #print(address)
        return address
        
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
      
    cnx = _connect.connect()
    cur = cnx.cursor() 
    cur.execute("""select * from vw_met_docs where id = ?""", mdId)
    return cur
 
   
def prepareCreators(mdId):
    #print("debug _metadata ln 174: doing prepareCreators")
    cnx = _connect.connect()
    cur = cnx.cursor()
    creators = []
    # First prepare named people
    # corrected for 2023
    # sql = 'select p.family_name, p.given_name, p.name_identifier, p.name_identifier_scheme, p.scheme_uri, o.name, o.street_address, o.address_locality, o.address_region, o.address_country, o.postal_code from (persons p inner join person_creators pc on p.id = pc.person_id) inner join organisations o on p.organisation_id = o.id where pc.metadata_document_id  = ?', mdId
    cur.execute("""select p.family_name, p.given_name, p.name_identifier, 
                p.name_identifier_scheme, p.scheme_uri, o.name, o.street_address, 
                o.address_locality, o.address_region, o.address_country, o.postal_code 
                from (persons p inner join person_creators pc on p.id = pc.person_id) 
                inner join organisations o on p.organisation_id = o.id 
                where pc.metadata_document_id  = ?""", mdId)
    
    results = cur.fetchall() 
     
    for row in results: 
        #print("debug _metadata ln193")
        #print(row)
        person = Person(row)  
        #print("debug _metadata ln 197")
        #print(person.asCreatorJson())
        creators.append(person.asCreatorJson())
        
    # ----   second prepare creator organisations --------  
    # corrected for 2023
    cur.execute("""select * 
                from organisations o 
                inner join organisation_creators oc on o.id = oc.organisation_id 
                where oc.metadata_document_id  =  ?""",mdId)
    results = cur.fetchall()
    
    for row in results:
        #print("debug _metadata ln208")
        #print(row)
        creators.append({"type": "organization", "name": row.name}) 
        
    return creators

def prepareContributors(mdId):
    #print("debug _metadata ln 214: doing prepareContributors")
    cnx = _connect.connect()
    cur = cnx.cursor()
    contributors = [] 
    # First prepare named people
    # corrected for db2json23 2023-04-28
    cur.execute("""select p.family_name, p.given_name, p.name_identifier, 
                p.name_identifier_scheme, p.scheme_uri, o.name, o.street_address, 
                o.address_locality, o.address_region, o.address_country, o.postal_code, 
                prt.type_value from ((persons p inner join organisations o on p.organisation_id = o.id) 
                inner join person_roles pr on p.id = pr.person_id) 
                inner join person_role_types prt on pr.person_role_type_id = prt.id 
                where pr.metadata_document_id = ?""", mdId)
    
    results = cur.fetchall()    
    for row in results: 
        #print("debug _metadata ln 232")
        #print(row) 
        person = Person(row)
               
        contributors.append(person.asContributorJson())
    # -----   second prepare organisations    ------------
    # we do not record organisations as contributors - only as creators
    # modified 2023-11-01 Nathcast
        
    return contributors    
    
def prepareSubjects(mdId):
    #print("debug _metadata ln 214: doing prepareSubjects")
    cnx = _connect.connect()
    cur = cnx.cursor()
    subjects = []
    # updated for db2json23 2023-04-28
    cur.execute("""select s.subject, s.uri, ss.name, ss.abbreviation, ss.uri 
                from (subjects s 
                inner join subject_schemas ss on s.subject_schemas_id = ss.id) 
                inner join document_subjects ds on s.id = ds.subject_id 
                where ds.metadata_document_id = ?""", mdId)
    results = cur.fetchall()    
    for row in results: 
        subjects.append(row.subject)
        
    return subjects
    
def prepareDescriptions(row):
    #print("debug _metadata ln 267: doing prepareDescriptions")
    descriptions = []
    # checked 2023-04-28 for db2json23
    descriptions.append({'inLanguage' : row.lang, 'descriptionType' : 'Abstract', 'description' : row.description_abstract})
    if not row.description_methods is None:
        descriptions.append({'inLanguage' : row.lang, 'descriptionType' : 'Methods', 'description' : row.description_methods})
    if not row.description_toc is None:
        descriptions.append({'inLanguage' : row.lang, 'descriptionType' : 'TableOfContents', 'description' : row.description_toc})
    if not row.description_technical_info is None:
        descriptions.append({'inLanguage' : row.lang, 'descriptionType' : 'TechnicalInfo', 'description' : row.description_technical_info})
    if not row.description_other is None:
        descriptions.append({'inLanguage' : row.lang, 'descriptionType' : 'Other', 'description' : str(row.description_other)})
    if not row.description_provenance is None :
        descriptions.append({'inLanguage' : row.lang, 'descriptionType' : 'Provenance', 'description' : str(row.description_provenance) })
    if not row.description_quality is None :
        descriptions.append({'inLanguage' : row.lang, 'descriptionType' : 'Quality', 'description' :  str(row.description_quality) })

    return descriptions

def prepareDateCreated(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    # corrected 2023-04-28 for db2json23
    cur.execute("""select dt.type_value , dd.document_date  
        from document_dates dd 
        inner join date_types dt on dd.date_type_id  = dt.id 
        where dd.metadata_document_id  = ?""", mdId)
    
    results = cur.fetchall()    
    for row in results: 
        if row.type_value == 'Created':
            return row.document_date.strftime('%Y-%m-%d')  

def prepareDateAvailable(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    # corrected 2023-04-28 for db2json23
    cur.execute("""select dt.type_value , dd.document_date  
        from document_dates dd 
        inner join date_types dt on dd.date_type_id  = dt.id 
        where dd.metadata_document_id  = ?""", mdId)
    
    results = cur.fetchall()    
    for row in results: 
        if row.type_value in ('Available', 'Accepted') :
            return row.document_date.strftime('%Y-%m-%d')  


def prepareDateModified(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    # corrected 2023-04-28 for db2json23
    cur.execute("""select dt.type_value , dd.document_date  
        from document_dates dd 
        inner join date_types dt on dd.date_type_id  = dt.id 
        where dd.metadata_document_id  = ?""", mdId)
    
    results = cur.fetchall()    
    for row in results: 
        if row.type_value == 'Updated' :
            return row.document_date.strftime('%Y-%m-%d')  
        
def getInfo(database_identifier):
    #print("debug _metadata ln 330: doing database_identifier")
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
    #print("debug _metadata ln 350: doing prepareRelatedIdentifiers")
    cnx = _connect.connect()
    cur = cnx.cursor()
    related_identifiers = []
    cur.execute("""select
	ri.identifier,
	ri.name as ri_name,
	ri.identifier_type_id  as identifier_type,
	r.display_value  as type_description,
	ri.relation_type_id  as rtID,
	r.type_value as relation_type
from
	related_identifiers ri
inner join relation_types r on
	ri.relation_type_id  = r.id
where
	ri.metadata_document_id = ?""", mdId)
    
    results = cur.fetchall() 
    ri_name_v = ''
    ri_type_v = 'Text'  
    for row in results:   
        RI_info = getInfo(row.identifier)
        if RI_info['title'] != 'NONE':
            ri_name_v =  RI_info['title']
            ri_type_v = RI_info['grt_value']
        else:
            ri_name_v =  row.ri_name
            ri_type_v = 'Text'
            
        related_identifiers.append({
            'relatedIdentifier': row.identifier,
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
    # checked and corrected  2023-04-28
    cur.execute("""select  du.name, df.size_value  
        from document_files df  inner join document_units du  on du.id  = df.document_unit_id  
        where df.metadata_document_id  = ?""", mdId)
    
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
    # checked and  corrected 2023-04-28
    cur.execute("""    select
	fa.reference_number ,
	fa.uri ,
	fa.title,
	o.name,
	o.funder_identifier,
	o.funder_identifier_type
from
	(document_funders df
inner join funding_awards fa on
	df.funding_award_id  = fa.id)
inner join organisations o on
	fa.organisation_id = o.id
where
	df.metadata_document_id  = ?""", mdId)

    results = cur.fetchall()
    for row in results:
        fundingreferences.append(
           {
               "type": "organization",
               "name": row.name,
               "sameAs": row.funder_identifier,
               "award":  row.reference_number + ' - ' + row.title,
               "identifier": row.uri
            }
        )
        
    return fundingreferences

def prepareDistribution(mdId):
    cnx = _connect.connect()
    cur = cnx.cursor()
    distribution = []
    # checked and  corrected 2023-04-28  
    rows_count = cur.execute("""SELECT
	df.id,
	df.metadata_document_id ,
	du.name ,
	df.size_value,
	df.file_name,
	df.title 
FROM
	document_files df 
left join document_units du  on
	df.document_unit_id  = du.id 
where
	df.is_illustration  = 0
	and df.metadata_document_id  = ?""", mdId)

    try:
        results = cur.fetchall()
        for row in results:
            
            fileName = row.file_name
            if fileName:
                fileParts = fileName.split(".")
                encodingFormat = fileParts[-1]
                distribution.append(
                {
                    "type": "dataDownload",
                    "name": row.title,
                    "URL": fileName,
                    "encodingFormat":  encodingFormat,
                    "fileSize": str(row.size_value) + ' ' + row.name
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
    # checked and  corrected 2023-04-28
    rows_count = cur.execute("""SELECT
	df.id,
	df.metadata_document_id ,
	du.name ,
	df.size_value,
	df.file_name,
	df.title 
FROM
	document_files df 
left join document_units du  on
	df.document_unit_id  = du.id 
where
	df.is_illustration  = 1 
	and df.metadata_document_id  = ?""", mdId)

    try:
        results = cur.fetchall()
        for row in results:
            
            fileName = row.file_name
            if fileName:
                fileParts = fileName.split(".")
                encodingFormat = fileParts[-1]
            else:
                encodingFormat = ''
            illustration.append(
                {
                    "type": "imageObject",
                    "caption": row.title,
                    "URL": fileName,
                    "encodingFormat":  encodingFormat,
                    "fileSize": str(row.size_value) + ' ' + row.name
                }
                )  
    except TypeError:
        illustration = []
    return illustration

def process(documentInfo):
    #print("debug _metadata ln 174: doing process")
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
            'inLanguage' : mdRow.lang,  
            'version' : str(mdRow.version), 
            'keywords' : prepareSubjects(mdId),
            'creator' : prepareCreators(mdId),
            'contributor' : prepareContributors(mdId),
            'encodingFormat' : mdRow.document_format_id,
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
                     'name': mdRow.field_name            
                 },
              'relatedIdentifier': prepareRelatedIdentifiers(mdId),
              'funder' : prepareFundingReferences(mdId),
              'distribution' : prepareDistribution(mdId),
              'image' : prepareIllustration(mdId),
             'grade': mdRow.grade if mdRow.grade   else 1,
             'isReady'      : mdRow.is_ready if mdRow.is_ready   else 1,
             'isExternal'   : mdRow.is_external if mdRow.is_external else 0,
             'dstype': mdRow.dataset_type if mdRow.dataset_type else 'N/A'
        }
        #print("debug _metadata line 597")
        #print(data)
        
    documentInfo.data = data    
    return documentInfo    

def prepMD(documentInfo):
    data = documentInfo.data
    folder = documentInfo.folder      
    # horizontal line is ---
    newline = '\n  '
    
    readme = f''
    readme += '\n  '
    readme += f"# {data['name']} ({data['identifier']})  " 
    readme += '\n' 
    readme += f"## Experiment Code:  [[experiment-{folder}]]  "  
    readme += '\n'
    for item in data['description']:
        readme += '\n  '
        readme += '***'
        readme += '\n  '
        readme += '\n  '
        readme += f"### {item['descriptionType']}  "
        readme += '\n  '
        readme += '\n  '
        readme += f"{item['description']}  "
    
    return readme

def prepRIS(documentInfo): 
    data = documentInfo.data
          
    # horizontal line is ---
    newline = '\n'
    readme = f''
    readme += f"TY  - DATA  " 
    readme += newline 
    readme += f"TI  - {data['name']} "
    readme += newline
    readme += f"CY  - {data['publisher']['name']} " 
    readme += newline
    readme += f"DB  - e-RA - the electronic Rothamsted Archive " 
    readme += newline
    readme += f"PY  - {data['publication_year']} "
    readme += newline 
    readme += f"DP  - Rothamsted Research, Harpenden, Herts, AL5 2JQ, UK. "    
    readme += newline 
    readme += f"M3  - {data['encodingFormat']} " 
    readme += newline
    readme += f"ET  - {data['version']} "
    readme += newline 
    readme += f"LA  - {data['inLanguage']} " 
    readme += newline
    readme += f"UR  - https://doi.org/{data['identifier']} "
    readme += newline 
    readme += f"DO  - {data['identifier']} "
    authorPerson = ''
    authorOrg = ''   
    for item in data['creator']: 
        if item['type'].lower() == 'person':
            
            authorPerson += newline
            authorPerson += f"AU  - {item['familyName']}, {item['givenName']} "        
        if item['type'].lower() == 'organization':
            
            authorOrg += newline
            authorOrg += f"AU  - {item['name']}, "      
    if  authorPerson == '':
        readme += authorOrg
    else: 
        readme += authorPerson  
    readme += newline
    readme += f"KW  - " 
    for item in data['keywords'] :
        if 'KeyRef' not in item:
            readme += f"{item}, "
        
    for item in data['description'] : 
        if item['descriptionType'] == 'Abstract':
            readme += newline
            readme += f"AB  - {item['description']} "
    readme += newline         
    readme += f"ER  -  " 
    
    return readme

def save(documentInfo): 
    #print("debug _metadata ln 612: doing save")
    if documentInfo.data['@type'][0].lower() == "t":
        datasetFolder = str(documentInfo.folder)
    else: 
        datasetFolder = str(documentInfo.folder)+"/"+ str(documentInfo.shortName)
    dirname =  settings.STAGE+ "metadata/"+datasetFolder
    AFolder.makeDir(dirname)
    repoName =  settings.REPO+ "metadata/"+datasetFolder
    AFolder.makeDir(repoName)
    strVersion = ""
    nbVersion = float(documentInfo.version)
    inVersion = int(nbVersion)
    if documentInfo.version is None:
        strVersion = "01"
    else: 
        if int(inVersion) <10: 
            strVersion = "0"+str(inVersion).lstrip('0')
        else:
            strVersion = str(inVersion) 
    xname = dirname +"/"+ strVersion + "-" + str(documentInfo.shortName) +".json"
    fxname = open(xname,'w+')
    strJsDoc =  json.dumps(documentInfo.data, indent=4)
    #print(strJsDoc)
    fxname.write(strJsDoc)
    fxname.close()
   
    mkdwn =prepMD(documentInfo)
    mdname = settings.STAGE+ 'markdownvault/dataset-'+documentInfo.folder+'-'+ strVersion + "-" + str(documentInfo.shortName) +".md"
    fxname = open(mdname,'w+')
    fxname.write(mkdwn)
    fxname.close()
    print("markdown file saved in  = " + mdname) 
    
    risRef =prepRIS(documentInfo)
    risname = dirname +"/"+ strVersion + "-" + str(documentInfo.shortName) +".ris"
    fxname = open(risname,'w+')
    fxname.write(risRef)
    fxname.close()
    print("ris file saved in  = " + risname)
    
    
    
def getDOCIDs():
    #list 
    DOCIDs = []
    cnx = _connect.connect()
    cur = cnx.cursor()
    cur.execute("""select * from vw_met_docs where grt_value like 'Dataset' order by 'url'  """)
    results = cur.fetchall()  
    counter = 0  
    for row in results: 
        
        counter +=1  
        DOCIDs.append(dict(
            nb = counter,
            documentID = row.id,
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
    #print("Debug _metadata ln 664")
    #print(documentInfo.mdId)
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
                #print("%s -  %s (%s) DOCIDs =  %s" % (counter, items['title'],items['expCode'], items['documentID']))
                IDs.append(str(items['documentID']))
                tokens.append(str(counter))
            #print(" ")  
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
                #print(datasetID)
            
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
    

