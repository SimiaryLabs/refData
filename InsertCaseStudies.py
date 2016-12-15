# For saving the processed output to disk
import numpy as np

import sys
sys.setrecursionlimit(100)

# For timing
import time

import json
from pprint import pprint

# Extracts the information from a single case study, creates a payload object containing the corpusID and API key ready to be sent
def case_study_insert_request(caseStudy, corpus_id, api_key):

    # Create payload structure
    payload = {}
    payload['properties'] = {}
    payload['properties']['type'] = "article"

    # Pteraforma API stuff
    payload['api_key'] = api_key
    payload['corpus'] = corpus_id
    payload['options'] = {
        'doTemporal': True,
        'doGeo': True,
        'doGeoboost': True
    }

    # Process bilographic header information
    payload['title'] = caseStudy["Title"]
    payload['properties']['CaseStudyId'] = caseStudy["CaseStudyId"]

    payload['properties']['Funders'] = caseStudy["Funders"] # funders.json

    payload['properties']['Panel'] = caseStudy["Panel"] # UnitOfAssessment.json (panel field)
    payload['properties']['UOA'] = caseStudy["UOA"] # UnitOfAssessment.json (subject field)

    payload['properties']['ResearchSubjectAreas'] = caseStudy["ResearchSubjectAreas"] # subjects.json

    payload['properties']['ImpactType'] = caseStudy["ImpactType"] # ImpactType.json
    payload['properties']['Institution'] = caseStudy["Institution"] # institutions.json

    payload['properties']['References'] = caseStudy["References"]
    payload['properties']['Sources'] = caseStudy["Sources"]

    payload['properties']['Continent'] = caseStudy["Continent"]
    payload['properties']['Country'] = caseStudy["Country"]
    payload['properties']['PlaceName'] = caseStudy["PlaceName"]
    payload['properties']['UKLocation'] = caseStudy["UKLocation"]
    payload['properties']['UKRegion'] = caseStudy["UKRegion"]


    ##
    ## Here are where the choices about how to strucutre the document go
    ## I have made it match the expected style, but it should be easy to change to just inserting a single paragraph for instance
    ##

    payload['sections'] = []

    ## Impact Summary
    sectionTitle = "Impact Summary"
    sectionType = "Impact Summary"
    sectionParagraphs = []
    sectionReferences = []
    payload['sections'].append({ "title": sectionTitle, "type": sectionType , "number": "0", "paragraphs": sectionParagraphs, "references": sectionReferences})

    ## Underpinning Research
    sectionTitle = "Underpinning Research"
    sectionType = "Underpinning Research"
    sectionParagraphs = []
    sectionReferences = []
    payload['sections'].append({ "title": sectionTitle, "type": sectionType , "number": "1", "paragraphs": sectionParagraphs, "references": sectionReferences})

    ## Impact Details
    sectionTitle = "Impact Details"
    sectionType = "Impact Details"
    sectionParagraphs = []
    sectionReferences = []
    payload['sections'].append({ "title": sectionTitle, "type": sectionType , "number": "2", "paragraphs": sectionParagraphs, "references": sectionReferences})


    # Return the Payload
    return payload


# Method for process the entire archive (change the glob regex to change that scope)
def process_case_studies(filename, api_key, corpus_id):

    # Measuring execution time
    start = time.time()

    dataArray = []
    maxNum = 7000;
    count = 0

    # Load JSON File
    with open(filename) as data_file:
        allStudies = json.load(data_file)

        # Loop over each case study in the json file
        for caseStudy in allStudies:
            # Creates the request object, this is the point of extension for integration with Pteraforma
            request = case_study_insert_request(caseStudy, corpus_id, api_key)

            # Logging code for feedback, remove if run in production
            if (count % 1000 == 0):
                print(count, time.time() - start)

            # Saving the result
            dataArray.append(request)

            # Implements a cut off number to processm, helpful for testing
            count = count + 1
            if (count > maxNum):
                break
    return dataArray


# parameters
api_key = "a1df798b5a10274bf32106303e91f05f"
corpus_id = 52
file_name = "allStudies.json"

dataArray = process_case_studies(file_name, api_key, corpus_id)
len(dataArray)
