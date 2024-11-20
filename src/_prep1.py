'''
Created on 1 Oct 2019
this interrogate the GLTN API to retrieve information about the experiments

@author: castells

'''

import requests
import settings
import _connect
import json
from pygments.lexers import sql
from operator import itemgetter 


class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)
    


def getGLTENIDs():
   
    cnx = _connect.connect()
    cur = cnx.cursor()
    GLTENIDs = []
    sql = 'SELECT  name, code,  glten_id, key_ref_code FROM experiments where glten_id is not null order by name;'
    cur.execute(sql)
    results = cur.fetchall()  

    for row in results: 
        GLTENIDs.append(dict(
                experiment_name = row.name,
                folder = row.code.replace('/','').lower(),
                GLTENID = row.glten_id, 
                KeyRef = row.key_ref_code
                ))
           
    return GLTENIDs

def getKeywords(folder): 
    expKW = ""
    sql = f"select DISTINCT  subject from subjects join document_subjects ds on ds.subject_id = subjects.id where ds.metadata_document_id in (select md2.id from metadata_documents md2 join experiments e on md2.experiment_id = e.id where e.folder = '{folder}')"
    cnx = _connect.connect()
    cur = cnx.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    for row in results: 
        expKW += row.subject.lower()
        expKW += ", "
    return expKW.rstrip(', ')


def getData(exptID):
    base = "https://glten.org/api/v0/public/experiment/"
    exptID = str(exptID)
    
    
    gltenData = requests.get(base + exptID)
    
    if gltenData.status_code != 200:
        # This means something went wrong.
        #raise APIError('GET /tasks/ {}'.format(gltenData.status_code))
        data = ' - '
        #for todo_item in resp.json():
        #print('{} {}'.format(todo_item['id'], todo_item['summary']))
    else :
        data =  gltenData.json()
        
    return data

def prepareRelatedExperiments(REdata):
    
    relatedExperiments = []
    if REdata:
        for detailRE in REdata:
            relatedExperiments.append(dict(
                type= "Experiment",
                identifier= "10.23637/Sax-rrn2-1 - that would be the DOI - Unique Identifier",
                localIdentifier= "rrn2 - Use the code for the experiment - Local Identifier",
                name= "Saxmundahm Rotation 2"
                ))
    else: 
        relatedExperiments = "NA"
    return relatedExperiments

def prepareFunders(data):
    funders = "NOT in GLTEN"
    
#     [
#         {
#             "type": "organization",
#             "name": "Biotechnology and Biological Sciences Research Council",
#             "sameAs": "http://dx.doi.org/10.13039/501100000268",
#             "award": "BBS/E/C/000J0300 - The Rothamsted Long - Term Experiments - National Capability",
#             "identifier": "https://gtr.ukri.org/projects?ref=BBS%2FE%2FC%2F000J0300",
#             "startDate": "2000",
#             "endDate": "2010"
#         },        {
#             "type": "organization",
#             "name": "Biotechnology and Biological Sciences Research Council",
#             "sameAs": "http://dx.doi.org/10.13039/501100000268",
#             "award": "BBS/E/C/000J0300 - The Rothamsted Long - Term Experiments - National Capability",
#             "identifier": "https://gtr.ukri.org/projects?ref=BBS%2FE%2FC%2F000J0300",
#             "startDate": "2000",
#             "endDate": "2010"
#         }
#     ]
    return funders

def prepareCitation(data):
    citation = []
    for details in data['literature']:
        citation.append(dict(
            type= "creativeWork",
            identifier= details['doi'],
            sameAs= details['doi'],
            citation= details['title'],
            inLanguage=  details['language'],
            relationType= "isCitedBy"
            
            ))

    return citation

def prepareExperiment(data):
    return dict(
    administrative= dict( 
        type= "ScholarlyArticle",
        identifier=  data['name'],
        localIdentifier=  data['local_identifier'],
        name= data['name'],
        url=  data['url'],
        description= data['description'],
        disambiguatingDescription= data['objective'],
        subjects = getKeywords(data['local_identifier'].replace('/','').lower()),
        #relatedExperiment= prepareRelatedExperiments(data['related_experiments'])
    ),
    dataAccess= dict(
        type= "creativeWork",
        conditionsOfAccess= data['data_statement_label'],
        isAccessibleForFree= data['data_policy_status'],
        publishingPrinciples= data['data_url'],
        actionableFeedbackPolicy= data['objective'],
        correctionsPolicy= data['objective'],
        unnamedSourcesPolicy= data['data_policy_url']
    ),
    license= dict(
        type= "CreativeWork",
        name= "CC0",
        license= "https://creativecommons.org/share-your-work/public-domain/cc0/"
    ),
    temporalCoverage= "1953/1970 from schema",
    dateStart= data['start_year'],
    dateEPEnd= data['establishment_period_end'],
    dateEnd= data['end_year'],
    funder= prepareFunders(data) ,
    citation = prepareCitation(data)
)
    
def prepareSoilProperties(data):
    soilProperties = []
    for details in data['site_soil_properties']:
        soilProperties.append(dict (  
            variableMeasured= details['variable_term'] if details['variable_term'] else details['variable_label'],
            isEstimated= details['is_estimated'],
            isBaseline= details['is_baseline'],
            valueReference= details['typical_value'],
            minValue= details['min_value'],
            maxValue= details['max_value'],
            minSampleDepth= details['min_depth'],
            maxSampleDepth= details['max_depth'],
            unitCode= details['unit_term'],
            unitText= details['unit_label'],
            refYear= details['reference_year'],
            measurementTechnique= "NOT IN GLTN",
            description= "NOT IN GLTN"
            )
        )
    return soilProperties


def prepareSite(data):
    return dict(
        
    administrative= dict (
        name=  data['site_name'],
        identifier=  data['site_local_code'],
        type = data['site_type_label'],
        doi=  data['site_doi'],
        visitsAllowed=  'Yes' if data['site_visits_allowed'] else 'No',
        visitingArrangements= data['site_visiting_arrangements'],
        description= data['site_history'],
        management= data['site_management']
    ),
    location= dict(
        addressLocality= data['site_locality'],
        addressRegion= data['site_region'],
        addressCountry= data['site_country'],
        geoLocationPoint= dict(
            pointLongitude= data['site_centroid_longitude'],
            pointLatitude= data['site_centroid_latitude']
            ),
        geoLocationPlace= data['site_country'],
        polygon= "NOT IN GLTEN",
        elevation= data['site_elevation'],
        elevationUnit= data['site_elevation_unit'],
        slope= data['site_slope'],
        slopeAspect= data['site_slope_aspect']
    ),
    soil= dict (
        soilTypeLabel= data['site_soil_type_label'],
        soilDescription= data['site_soil_description']
    ),
    soilProperty= prepareSoilProperties(data),
    climate= dict(
        name= data['site_climatic_type_label'],
        description= data['site_soil_description'],
        weatherStation= dict(
            weatherStationID= "NOT IN GLTEN",
            name= "NOT IN GLTEN",
            distance="NOT IN GLTEN",
            direction="NOT IN GLTEN"
            )
        )
        )

def preparePersons(data):
    contributors = []
    for details in data['people']:
        sname = details['name'].split() 
        #assuming name = givenName familyName
        contributors.append(dict
                            (  
                                type= "Person",
            jobTitle= details['role_term'] if details['role_term'] else details['role_label'],
            name= details['name'],
            givenName= sname[0],
            familyName= sname[1],
            sameAs= details['orcid'],
#             address= dict(
#                 type= "PostalAddress",
#                 streetAddress= "not in GLTEN",
#                 addressLocality= "not in GLTEN",
#                 addressRegion= "not in GLTEN",
#                 postalCode= "not in GLTEN",
#                 addressCountry= "not in GLTEN"
#             ),
            affiliation= dict (
                type= "Organization",
                name= "Rothamsted Research",
                address= "West Common, Harpenden, Hertfordshire, AL5 2JQ, United Kingdom"
            )
            )
                            )
    return contributors

def prepareLevel(leveldata):
    levels = []
    for leveldetails in leveldata:
        levels.append(dict(
            id= leveldetails['id'],
            name= leveldetails['factor_variant_label'],
                        amount= leveldetails['amount'],
                        unitCode= leveldetails['amount_unit_term'],
                        unitText= leveldetails['amount_unit_label'],
                        appliedToCrop= leveldetails['crop_id'],
                        dateStart= leveldetails['start_year'],
                        dateEnd= leveldetails['end_year'],
                        frequency= leveldetails['application_frequency'],
                        method= leveldetails['application_method_label'],
                        chemicalForm= leveldetails['chemical_form_label'],
                        notes= leveldetails['note']
            ))
    return levels

def prepareFactors(factordata):
    factors = []
    
    for factordetails in factordata:
        factors.append(dict(
            id= factordetails['id'],
            name =  factordetails['factor_term'] if factordetails['factor_term']  else factordetails['factor_label'] ,                 
            description = factordetails['description'],
            effect= factordetails['effect'],                 
            plotApplication= factordetails['plot_application'],
            level= prepareLevel(factordetails['levels'])             
     ))
    return factors

def prepareFCFactors (FCFactorData, factordata):
    FCFactors = []
    for FCFDetails in FCFactorData:
        factorName = ''
        levelNameCode = ''
        levelNameText = ''
        for item in factordata:                                  
            factorID = FCFDetails['factor_id']
            if factorID  > 0:          
                if item['id']==FCFDetails['factor_id']:
                    factorName = item['factor_term'] if item['factor_term'] else item['factor_label'] 
                    try:
                        if FCFDetails['factor_level_id']:
                            factorLevel = int(FCFDetails['factor_level_id'])
                            for levelitems in item['levels']:                                          
                                if levelitems['id'] == factorLevel:
                                    levelNameText = levelitems['factor_variant_term'] if  levelitems['factor_variant_term'] else 'NULL'
                                    levelNameCode =  levelitems['factor_variant_label'] if levelitems['factor_variant_label'] else 'NULL'
                    except ValueError:
                            
                        print("No Factor Level")
                
        FCFactors.append(dict(
        Factor= factorName,
        levelCode= levelNameCode,
        levelText = levelNameText,
        Comment= FCFDetails['comment']
        ))
    return FCFactors
    
def prepareFactorCombinations(factorcombinationData, factordata):
    factorCombinations = []
    if factorcombinationData:
        for FCDetails in factorcombinationData:
            preparedfactor= prepareFCFactors(FCDetails['members'],factordata) if FCDetails['members'] else "NA"
            factorCombinations.append(dict(
                name= FCDetails['name'],
                    dateStart= FCDetails['start_year'],
                    dateEnd= FCDetails['end_year'],
                    description= FCDetails['description'],
                    factor= preparedfactor 
            ))
    return factorCombinations

def prepareCrops(cropData):
    crops = []
    for detailCrop in cropData:
         
        crops.append(dict(
            id=detailCrop['id'],
            name= detailCrop['crop_term'] if detailCrop['crop_term'] else detailCrop['crop_label'],
            #identifier= detailCrop['crop_term'],
            sameAs= detailCrop['crop_label'],
            dateStart= detailCrop['start_year'],
            dateEnd= detailCrop['end_year']
            ))
    return crops

def preparePhases(phaseData):
    phases = []
    for phaseDetail in phaseData:
        phases.append(dict(
            samePhase= phaseDetail['same_phase'],
            crop= phaseDetail['crop_id'],
            description= phaseDetail['notes']
            ))
    return phases

def prepareCropRotations(rotationdata):
    # sort array using keys year start and year end
    rotationSorted = sorted(rotationdata, key = lambda i: (i['start_year'],  i['end_year'] if i['end_year'] else 0 )) 
    rotations = []
    for detailRotation in rotationSorted:
        preparedrotationPhases=preparePhases(detailRotation['phases']) if detailRotation['phases'] else "Not in GLTEN"
        rotations.append(dict(
            name= detailRotation['name'],
                dateStart= detailRotation['start_year'],
                dateEnd= detailRotation['end_year'],
                phasing= detailRotation['phasing'],
                isTreatment= detailRotation['is_treatment'],
                rotationPhases= preparedrotationPhases
            ))
    return rotations
''' {
                    "material": "AllCrops",
                    "crop_id": null,
                    "comment": "Crop grain yields at 85% dry matter for cereals, 90% dry matter for oilseeds and fresh weight for potatoes. No straw data.",
                    "collection_frequency": "annually",
                    "variable_label": "yield components",
                    "variable_term": "yield components",
                    "unit_label": "tonnes per hectare",
                    "unit_term": "t/ha",
                    "scale": null
                },'''
def prepareMeasurements(measurementData):
    measurements = []
    for detailMeasurements in measurementData:
        measurements.append(dict(
            variable= detailMeasurements['variable_term'] if detailMeasurements['variable_term'] else detailMeasurements['variable_label'],
            unitCode= detailMeasurements['unit_term'],
            unitText= detailMeasurements['unit_label'],
            collectionFrequency= detailMeasurements['collection_frequency'],
            scale= detailMeasurements['scale'],
            material= detailMeasurements['material'],
            description= detailMeasurements['comment'],
            crop = detailMeasurements['crop_id']
        ))
    return measurements

def prepareDesigns(data):
    designs = []
    item = 0
    for details in data['periods']:
        preparedcrops = prepareCrops(details['crops']) if details['crops'] else "NA"
        preparedcropRotations = prepareCropRotations(details['rotations']) if details['rotations'] else "NA"
        preparedfactor = prepareFactors(details['factors']) if details['factors'] else "NA"
        preparedfactorCombinations = prepareFactorCombinations(details['factor_combinations'], details['factors']) if details['factor_combinations'] else "NA"
        preparedmeasurements = prepareMeasurements(details['measurements']) if details['measurements'] else "NA"
        
        designs.append(dict ( 
        administrative = dict( 
            type= "experiment",
            identifier= details['name'],
            localIdentifier= details['name'],
            name= details['name'],
            url= details['name'],
            description= str(details['design_description']) if details['design_description'] else ''  + str(details['description']) if details['description'] else ''
        ),
        design = dict( 
            dateStart= details['start_year'],
            dateEnd= details['end_year'],
            description= details['description'],
            designType = details['design_type_term'],
            designTypeLabel = details['design_type_label'],
            studyDesign= details['name'],
            factorCombinationNumber= details['number_of_factor_combinations'] if details['number_of_factor_combinations'] else 'NA',
            numberOfBlocks = details['number_of_blocks'],
            numberOfPlots= details['number_of_plots'],
            numberOfReplicates= details['number_of_replicates'],
            numberOfSubplots= details['number_of_subplots'],
            numberOfHarvests = details['number_of_harvests_per_year'],            
#             area= "Experiment area",
#             areaUnit= "Experiment area units",
#             plotWidth= "Plot width",
#             plotWidthUnit= "Plot width Unit",
#             plotLength= "Plot length",
#             plotLengthUnit= "Plot length Unit",
#             plotArea= "Plot area",
#             plotAreaUnit= "Plot area Unit",
#             plotSpacing= "Plot spacing",
#             plotSpacingUnit= "Plot spacing Unit",
#             plotOrientation= "Plot orientation",
#             numberHarvest= "Number of harvests per year"
        ),
        crops = preparedcrops,
        cropRotations = preparedcropRotations,
        factor = preparedfactor,
        factorCombinations = preparedfactorCombinations,
        measurements = preparedmeasurements
        
        )
            )
        
        item += 1
    return designs

def prepareContactPoints(contactsData):
    contacts = []
    for details in contactsData:
        contacts.append(dict(
            contactType= details['contact_type'],
            description= details['value'])
            )
    
    return contacts


'''
"organizations": [
        {
            "id": 2524,
            "contacts": [],
            "role_term": "research organisation",
            "name": "Rothamsted Research",
            "name_uri": null,
            "abbreviation": null,
            "role_label": "research organisation"
        }
    ],
    '''
def prepareOrganization(data):
    orgs = []
    
    for details in data['organizations']:
        preparedRole = "NA"
        preparedRole = details['role_term'] if details['role_term'] else details['role_label']
     
            
        orgs.append(dict(
                type= "Organization",
                name= details['name'] if details['name'] else "NA" ,
                legalName= details['abbreviation'] if details['abbreviation'] else details['name'],    
                identifier= details['name_uri'] if details['name_uri'] else "NA" ,
                role= preparedRole,
                contactPoint= prepareContactPoints(details['contacts']) if details['contacts'] else 'NA'#,
                #startDate= details['contact_type'],
                #endDate= details['contact_type']
            ))
    
    return orgs
def prepReadme(data):
    
    spacer  = ' '*len(data['name'])
    deco = '*'*len(data['name'])*6
    newline = '\n'
    readme = f'{deco}{newline}{newline}'
    
    readme += f"{spacer}{data['name']} ({data['local_identifier']}) {newline}{newline}"
    readme += f'{deco}{newline}{newline}{newline}'
    
    readme += f'{newline}'
    readme += f'{newline}'
    readme += f'DESCRIPTION'
    if data['url']:
    
        readme += f"{newline} {data['url']}"
        
    readme += f"{newline}    {data['description']}"
    readme += f"{newline}    {data['objective']}"
    readme += f'{newline}'
    readme += f"{newline}    Experiment start = {data['start_year']}{newline}"
    readme += f"{newline}    Experiment end = {data['end_year']}"
    readme += f'{newline}'
    readme += f'{newline}'
    
    readme += f'CONDITION OF ACCESS {newline}'
 
    readme += f'EXPERIMENT DESIGN {newline}'
    
    return readme

def prepMD(data):
    # horizontal line is ---
    spacer  = ' '*len(data['name'])
    newline = '\n'
    folder = data['local_identifier'].replace('/','').lower()
    readme = f''
    readme += f"# {data['name']} ({data['local_identifier']})"   
    readme += f'\n## DESCRIPTION'
    if data['url']:
        readme += f"\n{newline}**URL**:  [{data['url']}]"
    readme += f"\n{data['description']}"
    
    readme += f"\n{data['objective']}"
    
    readme += f"\n- **Experiment start** = {data['start_year']}"
    readme += f"\n- **Experiment end** = {data['end_year']}"

    readme += f'\n---'

    readme += f'\n## CONDITION OF ACCESS'

    readme += f'\n---'

    readme += f'\n## EXPERIMENT DESIGN'

    readme += '\n---'

    readme += f'\n## References'
    for details in data['literature']:
        readme += f"\n - [{details['doi']}]({details['title']})"
    return readme

def process(exptID):
    data = getData(exptID)
    
    if data != ' - ':
        for items in GLTENIDs:
            if items['GLTENID']== exptID:
                folder = items['folder']
      
        print(folder)
        
        experiment = prepareExperiment(data) 
        experimentJson =  json.dumps(experiment, indent=4)
        xname = settings.STAGE+ "metadata/"+str(folder)+"/experiment.json"
        fxname = open(xname,'w+')
        fxname.write(experimentJson)
        fxname.close()
        print("experiment.json saved in  = " + xname)
          
        site = prepareSite(data)
        siteJson =  json.dumps(site, indent=4)
        xname = settings.STAGE+ "metadata/"+str(folder)+"/site.json"
        fxname = open(xname,'w+')
        fxname.write(siteJson)
        fxname.close()
        print("site.json saved in  = " + xname)
        
           
        persons = dict (contributors = preparePersons(data))
        personJson =  json.dumps(persons, indent=4)
        xname = settings.STAGE+ "metadata/"+str(folder)+"/person.json"
        fxname = open(xname,'w+')
        fxname.write(personJson)
        fxname.close()
        print("person.json saved in  = " + xname) 
        
        design = prepareDesigns(data)
        designsJson = json.dumps(design, indent=4)
        xname = settings.STAGE+ "metadata/"+str(folder)+"/design.json"
        fxname = open(xname,'w+')
        fxname.write(designsJson)
        fxname.close()
        print("design.json saved in  = " + xname) 
    
        orgs = prepareOrganization(data)
        orgsJson = json.dumps(orgs, indent=4)
        xname = settings.STAGE+ "metadata/"+str(folder)+"/orgs.json"
        fxname = open(xname,'w+')
        fxname.write(orgsJson)
        fxname.close()
        print("orgs.json saved in  = " + xname) 
    else: 
        print('DATA NOT READY')
    
if __name__ == '__main__':
    
    while True:
        exptID = 0
    
        GLTENIDs = getGLTENIDs()
        IDs = []
          
        for items in GLTENIDs:
            print (" %s (%s) GLTENID =  %s" % (items['experiment_name'],items['folder'], items['GLTENID']))
            IDs.append(items['GLTENID'])
        
        print(IDs)
        print('\n')
    
    
        while exptID == 0:
            val = input('Which experiment GLTENID? ')
            try: 
                exptID = int(val)
                if exptID  not in IDs:
                    print("not in the list")
                    exptID = 0
            except ValueError:
                print("No.. this is not a number: please choose a number from the list ")
      
        process(exptID)
        new_game = input("Would you like to do another one? Enter 'y' or 'n' ")
        if new_game[0].lower()=='y':
            playing=True
            continue
        else:
            print("Thanks for your work!")
            break
        
    