from frictionless import describe_package, describe_schema, describe_resource, Schema, Package, validate, exception
import os
import glob
import pandas as pd
import markdown
from shutil import rmtree
import _metadata as mdq
import re
import json


def camel_to_space(val):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2',val)


print ("--- have your xls file ready in a D:\code\data\ folder ---- ")

filename = input ("Filename including extension: ")
mdq_id = input ("metadata document ID (find this in the eracuration): ")
#id = "https://doi.org/"+input ("DOI: ")


#----------------------Code after this -------------------------------------
path = 'D:\\code\\data\\'

xls = pd.ExcelFile(path + filename)
pname = filename.split(".")[0]
os.chdir(path)
rmtree(pname,ignore_errors=True)
os.mkdir(pname)
os.chdir(pname)
pkgpath = path + pname + "/"
datapath = pkgpath


dfmd = xls.parse("fields_metadata") ## sheet name
dfmd.set_index(["resource","name"], inplace=True) 

##pd.set_option('precision', 3) doesn't work
print('-- 1. Create a CSV version of the Excel File --')

r = lambda x: (x.format)
for sheet_name in xls.sheet_names:
    print(sheet_name)
    if "_factor_data" in sheet_name:
        df = xls.parse(sheet_name, converters={"note":str, "sub_plot":str, "plot_id":str}) #added plot_id
        #print(df.dtypes)
        df.to_csv(datapath + sheet_name + ".csv",index=False)
    elif "_dimension_data" in sheet_name:
        # IMPORTANT, NAs and floats cause problems. By default float fields with missing values are loaded as object data types. This is a problem because of floating point
        # errors which can't be corrected by float format (because object). To correct this need to specify the missing value type on the Excel parse, but this removes the missing
        # value value. This creates Frictionless validation problems. Pandas will allow the missing values to be retained, but the field reverts to object so doesn't work. 
        # the work around is use the na_rep to force missing values back in but this does it for all missing values, not valid missing values. Hence the if/else to only do this on the main 
        # data table   
        df = xls.parse(sheet_name, na_values="*", converters={"note":str, "sub_plot":str, "plot_id":str, "plot":str}) #added plot_id
        #print(df.dtypes)
        df.to_csv(datapath + sheet_name + ".csv",index=False, float_format="%.3f", na_rep="*")

    elif "_data" in sheet_name:
        # IMPORTANT, NAs and floats cause problems. By default float fields with missing values are loaded as object data types. This is a problem because of floating point
        # errors which can't be corrected by float format (because object). To correct this need to specify the missing value type on the Excel parse, but this removes the missing
        # value value. This creates Frictionless validation problems. Pandas will allow the missing values to be retained, but the field reverts to object so doesn't work. 
        # the work around is use the na_rep to force missing values back in but this does it for all missing values, not valid missing values. Hence the if/else to only do this on the main 
        # data table   
        df = xls.parse(sheet_name, na_values="*", converters={"note":str, "sub_plot":str, "plot_id":str, "plot":str}) #added plot_id
        #print(df.dtypes)
        df.to_csv(datapath + sheet_name + ".csv",index=False, float_format="%.3f", na_rep="*")

print("-- 2. Generate template metadata inferring from the CSV --")

## 2. Generate template metadata inferring from the CSV
pkg = describe_package(datapath, expand=True, stats=True) # works
## pkg.to_json("datapackage-prev.json")   # added by Nath to check what pkg looks like 2021-12-10

##pkg = Package(datapath+"/*")
##pkg.infer(stats=True)

pkg.profile = "tabular-data-package"
print("-- 3. Update the metadata for each data resource - TABS --")
## 3. Update the metadata for each data resource

for res in pkg.resources:
    rname = res["name"]
    print("Resource - rname: "+ rname)
    keys = []
    for fld in res.schema.fields:
        fname = fld["name"].strip()
        print("field - fname: " + fname)
        md = dfmd.loc[(rname,fname)]
        #if isinstance(md, pd.DataFrame):
        #   md = md.squeeze()
        # print(type(md))
        #print(md)
        if rname == 'crop_data':
            print("md: " + md)
        ## may have to replace with if pd.Series.item(md.title):            
        ## fld.title = pd.Series.item(md.title).strip()
        if not pd.isna(md.title):            
            fld.title = md.title.strip()
        #print("i")
        if not pd.isna(md.type):
            fld.type = md.type.strip()
        #print("ii")
        if not pd.isna(md.rdfType):
            fld.rdf_type = md.rdfType.strip()
        #print("iii")
        if not pd.isna(md.format):
            fld.format = md.format.strip()        
        #print("iv")
        if not pd.isna(md.description):
            fld.description = md.description.strip()
        #print("v")
        if not pd.isna(md.missingValues):
            fld.missing_values = [md.missingValues.strip()]
        #print("vi")
        # test for foriegn keys       
        if not pd.isna(md.constraints):
        #    print("vi-a")
            if md.constraints == 'primary key':
                res.schema.primary_key = fname
        #        print("vi-b")
            else:
        #        print("vi-c")
                fkparts = md.constraints.split('.')
        #        print("vi-d")
                if len(fkparts) == 2: 
        #            print("vi-a")
                    keys.append({'fields':fname,'reference': {'resource':fkparts[0],'fields':fkparts[1]}})
        #            print("vi-f')
                else:
        #            print("vi-g")
                    mdarr = md.constraints.replace(", ",",").strip().split(",")
                    # if the first value is a digit:
                    if (mdarr[0].isdigit()):
                        imdarr = [int(i) for i in mdarr]
                        fld.constraints = imdarr    
                    else:
                        fld.constraints = mdarr
        #            print("vi-h")
        #    print("vi-j")
        #print("vii")
    if keys:
        res.schema.foreign_keys = keys
try:
    valid = validate(pkg)
    print("+++++++++++ VALID +++++++++++")
   # print(json.dumps(valid, indent=4))
   # print("VALID++++++++++++++++++++++++")
except exception.FrictionlessException as e:
    print("+++++++++++ INVALID+++++++++++++")
    print(json.dumps(e.error, indent=4))
    print("+++++++++++ INVALID++++++++++++++")

print('--- 4. Add additional metadata to the package from README page --- ')
## 4. Add additional metadata to the package
# pkg.id = id
rm = xls.parse("README")
rm.columns = ["a", "b", "c"]

# simplest way to generate the README is to extract text from Excel into strings then process the JSON metadata and assemble blocks.
doi = ""
title = "" 
desc = ""
resource_table = ""
conditions_of_use = ""
rights_holder = ""
licence = ""
cite_as = ""
sup_material = ""

part = 1

## This gets the DataCite Metadata record
ds = mdq.get_document_json(mdq_id)

doiURL = 'https://doi.org/'+ds["identifier"].lower()
doi = ds["identifier"].lower()
title = ds["name"].strip()

def prepCitation (ds):
    #YOU MUST CITE AS: Glendining, M.J., Gregory, A. S., Poulton, P.R. and Wilmer, W. 
    # (2024). 
    # Hoosfield Spring Barley Experiment organic manure chemical composition 1852-2019. 
    # Electronic Rothamsted Archive, Rothamsted Research, Harpenden UK 
    # https://doi.org/10.23637/rhf2-fym-01	   
    data = ds
    authorPerson = ''
    authorOrg = '' 
    citation = f''
    for item in data["creator"]: 
        if item["type"].lower() == 'person':
            authorPerson += f'{item["givenName"]} {item["familyName"]}, '        
        if item["type"].lower() == 'organization':
            authorOrg += f'{item["name"]}, '      
    if  authorPerson == '':
        citation += authorOrg
    else: 
        citation += authorPerson 
    citation.rstrip(',')
    citation += f' ({data["publication_year"]}) '    
    citation += f'Dataset: {data["name"]}   _electronic Rothamsted Archive, Rothamsted Research, Harpenden, UK,_ '
    if '10.' in data["identifier"]:
        realURL = f' https://doi.org/{data["identifier"]} '
    else:  
        realURL = f'{data["url"]} '
    citation += f' {realURL}'
    return citation

for itemDesc in ds["description"]:
    if itemDesc["descriptionType"] == "Abstract":
        desc = itemDesc["description"]
        desc = desc.replace('\r', '').replace('\n', '')
        description = desc

## Loop through the Excel and extract content to local vars for later assembly
for idx, row in rm.iterrows():
    a = str(row["a"])
    b = str(row["b"])
    c = str(row["c"])
    # if a.startswith("README"):
    #     if b.startswith("http"): 
    #         doiURL = b
    #         doi = b.strip("https://doi.org/")
    #     else: 
    #         doiURL = "https://doi.org/"+b
    #         doi = b
            
    # elif a == "Title:":
    #     title = b.strip()
     
    # TODO   

    cite_as = prepCitation (ds)
    # elif a == "Description:":
    #     description = b.strip()
        
    ## we keep resource description
    if "resource descriptions" in a.lower():
        resource_table = "\n### Resource Descriptions\n\n|resource_id|resource_title|resource_description|\n|----|------------|-----------|\n"
        part = 2
    elif a == "resource_id" or a == "resource_name" or a == "resource name":
        pass    
    ## This is the descriptions: still taken from the XL - 
    ## TODO : Understand and action pkg stuff 
    elif part == 2 and str(a) != "nan":
        pkg.get_resource(a).title = b
        pkg.get_resource(a).description = c
        resource_table = resource_table + "|" + a + ".csv|" + b + "|" + c + "|\n"
        
    # elif a == "Conditions of Use:":
    #     part = 0
    
    # elif a == "Supplementary materials:":
    #     sup_material = "\n### Supplementary materials\n\n|Resource|link|description|\n|-------------|------------|-----------|\n"
    #     part = 3

    
    
    # elif part == 1 and str(a) != "nan":
    #     desc = desc + b    

    
    ## Suplementary stuff taken from database
    # elif part == 3 and str(a) != "nan":
    #     if 'http' in b: 
    #         sup_material = sup_material + "|" + a + "|[" + b + "](" + b + ")|" + c + "|\n"
    #     else: 
    #         sup_material = sup_material + "|" + a + "|[https://doi.org/" + b + "](https://doi.org/" + b + ")|" + c + "|\n"
            

## test 2024-08-27 NC
##print (json.dumps(ds, indent=4))
with open(pkgpath + "README.txt", "w") as readme:
    pkg.id = doi
    pkg.name = title.strip().replace(" ","-").lower()
    pkg.title = title.strip()
    
    readme.writelines("\n# README \n")
    readme.writelines("\n## Summary \n")
    readme.writelines("| <!-- -->    | <!-- -->    |\n")
    readme.writelines("|-------------|-------------|\n")
    readme.writelines("| **DOI**     |[" + doiURL + "](" + doiURL + ") |\n")
    readme.writelines("| **Title**   |"+ title + "|\n")
    readme.writelines("| **Version** |"+ str(ds["version"]) + "|\n")
    pkg.version = "1.0.0"
    readme.writelines("| **Published** |"+ str(ds["publication_year"]) + "|\n")
    readme.writelines("| **Publisher** |" + ds["publisher"]["name"] + "|\n")
    readme.writelines("| **Keywords**  |" + ", ".join(ds["keywords"]) + "|\n")
    pkg.keywords = ds["keywords"]
    readme.writelines("| **Cite as**   |" + cite_as + "|\n")
    readme.writelines("| <!-- -->   |This dataset is provided by e-RA, the electronic Rothamsted Archive, and the Rothamsted Long Term Experiments |\n")
    readme.writelines("| <!-- -->   |[https://www.era.rothamsted.ac.uk](https://www.era.rothamsted.ac.uk) |\n")
    readme.writelines("| **Summary**   |" + desc + "|\n")
    readme.writelines("| **Note**      |" + "The Excel file: _*" + filename + "*_ contains the same data as the CSV files. The Excel worksheet fields_metadata contains column descriptions for all the resources. Each _data suffix worksheet is a data resource. The data resources for this dataset are described below. For all other information refer to the landing page or machine readable metadata.json")
    readme.writelines("\n")
    readme.writelines(resource_table)
    readme.writelines("\n")
    description = ""
    for desc in ds["description"]:
        if desc["descriptionType"] != "TableOfContents":
            description = description + "### " + camel_to_space(desc["descriptionType"]) + "\n" 
            description = description + desc["description"].strip() + "\n\n"
    pkg.description = description
    readme.writelines(description)

    
    tblAuthor = "\n### Authors\n"+"|Name|ORCID|Affiliation|\n"+"|----|-----|-----------|\n"
    #readme.writelines("\n### Authors\n")
    #readme.writelines("|Name|ORCID|Affiliation|\n")
    #readme.writelines("|----|-----|-----------|\n")
    for auth in ds["creator"]:
        if auth["type"] == "Person":
            readme.writelines(tblAuthor)
            readme.writelines("|" + str(auth["Name"]) + "|<" + str(auth["sameAs"]) + ">|" + str(auth["affiliation"]["name"]) + "|\n")
            tblAuthor = ""

    readme.writelines("\n### Contributor Roles\n")
    readme.writelines("|Name|ORCID|Role (Affiliation)\n")
    readme.writelines("|----|-----|------------------|\n")
    contributors = []
    for auth in ds["contributor"]:
        # print (auth)
        # print ('\n')
        if auth["type"] == "Person":
            authURL = ""
            if "http" in str(auth["sameAs"]): 
                authURL = "<" + str(auth["sameAs"]) + ">"
    
            readme.writelines("|" + str(auth["name"]) + "|" + authURL+ "|" + camel_to_space(str(auth["jobTitle"])) + " (" + str(auth["affiliation"]["name"]) + ")|\n")
            contrib = {}
            contrib["title"] =  auth["name"]
            contrib["path"] = ""
            if auth["sameAs"]:
                contrib["path"] =  auth["sameAs"].strip().replace("<","").replace(">","")
            contrib["organization"] = auth["affiliation"]["name"]
            contributors.append(contrib)
    pkg.contributors = contributors
    
    readme.writelines("\n### Supplementary Material\n")
    readme.writelines("\n|Resource|link|description|")
    readme.writelines("\n|-------------|------------|-----------|\n")
    for ref in ds["relatedIdentifier"]:
        # {
        #     "relatedIdentifier": "10.23637/ERADOC-1-191",
        #     "relatedIdentifierType": "DOI",
        #     "name": "Rothamsted (1966) Details of the Classical Experiments",
        #     "relatedIdentifierGeneralType": "Text",
        #     "relationType": "IsDerivedFrom",
        #     "rt_id": 28,
        #     "relationTypeValue": "is derived from"
        # },
        # "|" + a + "|[https://doi.org/" + b + "](https://doi.org/" + b + ")|" + c + "|\n"
        if 'http' in ref["relatedIdentifierType"]: 
            readme.writelines("|"+ref["relatedIdentifierGeneralType"]+"| [" +  ref["relatedIdentifier"] + "](" + ref["relatedIdentifier"] + ")|" + ref["name"] + "|\n")
        else : 
            readme.writelines("|"+ ref["relationTypeValue"] + " " +ref["relatedIdentifierGeneralType"]+ "|[https://doi.org/" + ref["relatedIdentifier"] + "](https://doi.org/" + ref["relatedIdentifier"] + ")|" + ref["name"] + "|\n")
    readme.writelines("\n")
    readme.writelines("\n")      
        
    
    readme.writelines("\n### Conditions of Use\n")
    readme.writelines("| <!-- -->    | <!-- -->    |\n")
    readme.writelines("|-------------|-------------|\n")
    readme.writelines("|**Rights Holder**|    Rothamsted Research |\n")
    readme.writelines("|**Licence**|    This dataset is available under a Creative Commons Attribution Licence (4.0). [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/)|\n")
    pkg.licenses = [{"name":"CC-BY-4.0","path":"https://creativecommons.org/licenses/by/4.0/","title":"Creative Commons Attribution 4.0 International"}]
    readme.writelines("|**Cite this Dataset**|    " + cite_as + "|\n")
    readme.writelines("|**Conditions of Use**|    Rothamsted relies on the integrity of users to ensure that Rothamsted Research receives suitable acknowledgment as being the originators of these data. This enables us to monitor the use of each dataset and to demonstrate their value. Please send us a link to any publication that uses this Rothamsted data.|\n")

    readme.writelines("\n### Funding\n")
    readme.writelines("\nRothamsted Research receives strategic funding from the Biotechnology and Biological Sciences Research Council of the United Kingdom (BBSRC) and is also supported by the Lawes Agricultural Trust. We acknowledge support from the following:		")
    readme.writelines("\n\n")
    readme.writelines("|Grant Name|Funder|Grant Number- Work Packages |\n")
    readme.writelines("|----|-----|-----------------|\n")
    for fund in ds["funding"]:
        prefixes = ['https:','ror.org', 'doi.org']
        funder_id = ""
        funder_id_type = ""
        strList = fund["funder"]["identifier"].split('/')
        for item in strList:
            if item == 'ror.org': 
                funder_id_type = ' -  ROR_ID = '
            if item == 'doi.org': 
                funder_id_type = ' -  DOI = '    
            if item not in prefixes: 
                funder_id += item
        grantNumber = "" 
        if fund["url"]:
            grantNumber = "[" + fund["alternateName"] + "](" + fund["url"] + ")"
        else:
            grantNumber = fund["alternateName"] 
        workPackages = "N/A"
        if fund["disambiguatingDescription"] and "[" not in fund["disambiguatingDescription"]: 
            workPackages = fund["disambiguatingDescription"].strip().replace("["," ").replace("\"","").replace("  "," ").replace("]"," ")
            
        readme.writelines("|" + str(fund["name"]) + "|[" + fund["funder"]["name"] + "](" + fund["funder"]["url"] + ")"+ funder_id_type +funder_id + "|" + grantNumber + " - " + workPackages + "|\n")
   
        # readme.writelines("\n**Funder name**\n:    [" + fund["funder"]["name"] + "](" + fund["funder"]["url"] + ")\n")
        # readme.writelines("\n**Award**\n:    " + fund["name"] + "\n")
        # readme.writelines("\n**Award info**\n:    " )

    #pkg.funding = funding
    readme.writelines("\n")
    # we add the LAT line for the internal datasets
    if ds["isExternal"] == 0 : 
        #readme.writelines("\nThe RLTE-NBRI is also supported by the Lawes Agricultural Trust.")
        readme.writelines("\n")

    ## readme.writelines(sup_material)

    ## data dictionary
    readme.writelines("\n### Data Dictionary\n")
    
    for res in pkg.resources:
        print(res) #Check res as there is an issue
        readme.writelines("\n### " + res.name + "\n ")
        readme.writelines("\n#### " + res.title + "\n ")
        readme.writelines("\n" + res.description + "\n\n")
        readme.writelines("|Name|Title|Type|format|rdfType|Description|\n")
        readme.writelines("|----|-----|----|------|-------|-----------|\n")
        for fld in res.schema.fields:
            print(fld.name)
            readme.writelines("|"+fld.name+"|"+fld.title+"|"+fld.type+"|"+fld.format)
            if fld.rdf_type:
                readme.writelines("|["+fld.rdf_type+"]("+fld.rdf_type+")")
            else:
                readme.writelines("|")
            if fld.description:
                # print(fld.description)
                readme.writelines("|"+fld.description)
            else:
                readme.writelines("|")
            readme.writelines("|\n")

        readme.writelines("\n")

with open(pkgpath + "README.txt", "r") as input_file:
    text = input_file.read()
html = markdown.markdown(text, extensions=['tables','def_list'])

with open(pkgpath + "README.html", "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
    output_file.write("<html><head><style> " + 
        "body {font-family:calibri;} " +
        "table {border-collapse: collapse;} " +
        "table, th, td {border:1px solid darkgreen;}  " +
        "th, td {padding:8px;}  " +
        "th {background-color:#4CAF50;}  " +
        "tr:nth-child(even){background-color: #f2f2f2;}</style></head><body>")
    output_file.write(html)
    output_file.write('</body></html>')

#pkg.to_yaml(pname + ".yaml")
pkg.to_json("datapackage.json")
try:
    valid = validate(pkg)
    print("================ VALID datapackage PACKAGE ==================")
    with open(path + "err.json", "w") as err_file:
        err_file.write(json.dumps(valid, indent=4))
    #print(json.dumps(e.error, indent=4))
    print("================ VALID datapackage JSON ==================")
except exception.FrictionlessException as e:
    print("================ INVALID PACKAGE ==================")
    print(json.dumps(e.error, indent=4))
    print("================ INVALID JSON ==================")
    
print("++++++++++  create Field Metadata .csv ++++++++++++++++++++")
dfmd.to_csv(datapath + "fields_metadata" + ".csv",index=False)
print("================ That's all ==================")
print("Your Data package is in D:/code/data ")
print("Remember to set XLS tab to be README before saving ")

