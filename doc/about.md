# About

A set of Json tools to populate the newERA web site with data from a few databases. We are in the process of putting everything under one database. 

	- List of Experiments, datasets and documents are taken from the datacite database
	- Images are taken from the timeline database (to be moved)
	- Timelines are taken from the timeline database (to be moved)



## How to use: 

Running all the commands will rebuild the whole site json files and folders from the databases. 

	- Update the config file with a new staging area
	- Run AFolder: this creates the experiment folders and default folders, and the default/experiments.json file. It also in parallel, updates or creates the REPO  a template for the data repository on SALT or whereever we want it. l
	- Run updateMenu: this makes the menu with the experiments that are in GLTENID, saves in includes. Run with new experiment
	- run BExpts: this makes all the .json files for the website for all the experiments that are in the database.
		- if only updating one, use prep1: does one experiment at a time  
	- Run CData prepare datasets folders and json files or documents folders and json files. It also makes the foldes for the datasets in the REPO area . NOTE REGARDING prepDATA. it is easy to use, however, I am aware that the code is ugly and convoluted: it;s patchwork code and could do with redoing... 
	- use images2json to prepare the images.json file (still in the access db)
	- use timeline2json to prepare the timelines.json files (these are stored in relevant experiment folder)


## Naming conventions

	- Experiment folders are the experiment codes stripped of the / ro R/BK/1 (broadbalk) becomes rbk1
	- So far, DOIs have 
	
	Resource Unique Identifier (DOI)


## DEVELOPEMENT TO DOO
	- move the images2json to the datacite db 
	- move timeline tool to datacite db
	- name convention for datasets and documents	
	- when we have information about Station in the database, we will have to
	- where are the original document files??? How do we check them, update them from original location? 
	- decide where we save the documents: in a massive folder? in experiment folder? in dataset folder? As the document json file only info about the document and the URL, I am even questioning its validity
	- A tool to check that all the files needed are in the LIVE REPO. 
	- A tool to check that all the DOIed files are in their correct locations on the web site. .



> Written with [StackEdit](https://stackedit.io/).