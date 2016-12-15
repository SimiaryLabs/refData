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


#
# Methods to help generate counts
#

def populate_impact_types():
    # Load JSON File
    with open("ImpactType.json") as data_file:
        ImpactTypes = json.load(data_file)
        print("ImpactTypes", len(ImpactTypes))
        return ImpactTypes

def populate_subjects():
    # Load JSON File
    with open("subjects.json") as data_file:
        Subjects = json.load(data_file)
        print("Subjects", len(Subjects))
        return Subjects

def populate_units_of_assessment():
    # Load JSON File
    with open("UnitOfAssessment.json") as data_file:
        UnitOfAssessment = json.load(data_file)
        print("UnitOfAssessment", len(UnitOfAssessment))
        return UnitOfAssessment

def populate_funders():
    # Load JSON File
    with open("funders.json") as data_file:
        Funders = json.load(data_file)
        Funders.append({"ID": 50000, "Name": "None Specified"})
        print("Funders:", len(Funders))
        return Funders

def populate_institutions():
    # Load JSON File
    with open("institutions.json") as data_file:
        Institutions = json.load(data_file)
        print("Institutions", len(Institutions))
        return Institutions

def extend_reference_lists(ImpactTypes, Subjects, UnitOfAssessment, Institutions, Funders):

    ### FUNDERS
    for funder in Funders:
        funder["Institutions"] = []
        for institution in Institutions:
            funder["Institutions"].append({"InstitutionName": institution["InstitutionName"], "UKPRN": institution["UKPRN"], "Count": 0})

        funder["ImpactAreas"] = []
        for impact in ImpactTypes:
            funder["ImpactAreas"].append({"ID": impact["ID"], "Name": impact["Name"], "Count": 0})

        funder["SubjectAreas"] = []
        for subject in Subjects:
            funder["SubjectAreas"].append({"ID": subject["ID"], "Name": subject["Name"], "Count": 0})

        funder["CaseStudies"] = []


    ### INSTITUTIONS
    for institution in Institutions:
        institution["Funders"] = []

        for funder in Funders:

            funderImpacts = []
            for impact in ImpactTypes:
                funderImpacts.append({"ID": impact["ID"], "Name": impact["Name"], "Count": 0})

            funderSubjects = []
            for subject in Subjects:
                funderSubjects.append({"ID": subject["ID"], "Name": subject["Name"], "Count": 0})

            CaseStudies = []

            institution["Funders"].append({ "Name": funder["Name"], "ImpactAreas": funderImpacts, "SubjectAreas": funderSubjects, "CaseStudies": [] } )

#
# Script Begins
#

# Populate all the reference lists

ImpactTypes = populate_impact_types()
Subjects = populate_subjects()
UnitOfAssessment= populate_units_of_assessment()
Institutions = populate_institutions()
Funders = populate_funders()
extend_reference_lists(ImpactTypes, Subjects, UnitOfAssessment, Institutions, Funders)

# Pteraform Parameters
api_key = "a1df798b5a10274bf32106303e91f05f"
corpus_id = 52

dataArray = process_case_studies("allStudies.json", api_key, corpus_id)
len(dataArray)
