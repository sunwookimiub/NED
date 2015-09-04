"""
Accept a directory as input and generate preset files for NED data.
"""
import os
import re
import csv
import json
import fiona
import argparse
import subprocess

# --------------------------- Get the Boundaries -------------------------
def generateBoundaries(inputDir, output, secondDir):
    """
    Generate the boundaries.json file

    Parameters:
    -----------
    inputDir:       - The input directory [/gpfs_scratch/ned_data_boundaries/\
                                           HUC/HUC2/geojson/]
    output:         - Name of the output boundaries file
    secondInputDir: - Name of a second input directory
    """
    count = 0
    js_lists = []
    getBnds(inputDir, js_lists)
    getBnds(secondDir, js_lists)
    with open(output, 'wb') as json_file:
        json.dump(js_lists, json_file, indent=4)

def getBnds(dir, js_lists):
    """
    Return the array with boundary information

    Parameters:
    -----------
    dir:        - The directory containing the geojson files
    js_lists:   - The array to append the information onto
    """
    # Retrieve set = [HUC or State]
    set = dir.split("/")[4]
    if "geojson" in set:
        set = dir.split("/")[3]
    for fn in os.listdir(dir):
        fullPath = os.path.join(dir, fn)
        nameWOSuffix = fn.split(".")[0] # Name of file without suffix
        if checkIfRelevant(set, nameWOSuffix):
            with fiona.open(fullPath, 'r') as src:
                # Go through all the layers
                for layer in src:
                    id = "{}_{}".format(set, nameWOSuffix)
                    name = "{}_{}".format(set, nameWOSuffix)
                    desc = "This is the boundary for {}".format(name)
                    with open(fullPath, 'r') as test:
                        shape = "'" + str(json.load(test)) + "'"
                    keywords = []
                    if "HUC" in set:
                        kw = "HUC"
                    else:
                        kw = nameWOSuffix
                    keywords.append(kw)
                    js_up = {"_id": id, "visible": "true", "name": name,\
                              "description": desc, "projection": "EPSG:4269",\
                              "shape": shape, "keywords": keywords}
                    js_lists.append(js_up)

def checkIfRelevant(set, nameWOSuffix):
    """
    Check whether to include certain files in the HUC directories since we do
    not wish to include HUC2's 19-22 geojson files and HUC4's geojson files 
    above 1900.

    Parameters:
    -----------
    set:            - The name of the set [HUC or State]
    nameWOSuffix:   - Name of the file without suffix. [IL.geojson -> IL]  
    """
        isRel = True
        if set == "HUC2":
            if re.search('[a-zA-Z]', nameWOSuffix) != None:
                isRel = False
            elif int(nameWOSuffix) > 18:
                isRel = False
        if set == "HUC4":
            if re.search('[a-zA-Z]', nameWOSuffix) != None:
                isRel = False
            elif int(nameWOSuffix) > 1810:
                isRel = False
        return isRel


# --------------------------- Get the Products --------------------------------
def generateProducts(inputDir, output, secondDir=None):
    """
    Generate the products.json file

    Parameters:
    -----------
    inputDir:       - The input directory [/gpfs_scratch/ned_data_boundaries/\
                                           HUC/HUC2/geojson/]
    output:         - Name of the output sources file
    secondInputDir: - Name of a second input directory
    """
    js_lists = []
    createProd(inputDir, js_lists)
    createProd(secondDir, js_lists)
    with open(output, 'wb') as json_file:
        json.dump(js_lists, json_file, indent=4)

# Just a dictionary of states to get the name of the state from abbreviations
states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

def createProd(dir, js_lists):
    """
    Create the products with the required specifications and append them onto
    one single array.

    Parameters:
    -----------
    dir:        - The directory to look through for geojson files
    js_lists:   - The array to append onto
    """
    source = "USGS_NED_DATA"
    r = "-1"
    # Set = HUC or State
    set = dir.split("/")[4]
    if "geojson" in set:
        set = dir.split("/")[3]
    for fn in os.listdir(dir):
        nameWOSuffix = fn.split(".")[0]
        title = set + "_" + nameWOSuffix
        boundary = title
        if boundary != None:
            js_up = {"visible": "true", "title": title, "public": \
                    "true", \
                    "input": {"source": source, "boundary": boundary, \
                    "projection": "proj_4269", "resolution": [r,r], \
                    "products": {"slope": "true", "hillshade": "true", \
                    "pitremove": "false"}, "resamplingMethod": \
                    "bilinear",
                    "fileFormat": "GTiff"}}
            js_lists.append(js_up)

            js_up = {"visible": "true", "title": title, "public": \
                    "true", \
                    "input": {"source": source, "boundary": boundary, \
                    "projection": "proj_3857", "resolution": [r,r], \
                    "products": {"slope": "true", "hillshade": "true", \
                    "pitremove": "false"}, "resamplingMethod": \
                    "bilinear",
                    "fileFormat": "GTiff"}}
            js_lists.append(js_up)

            js_up = {"visible": "true", "title": title, "public": \
                    "true", \
                    "input": {"source": source, "boundary": boundary, \
                    "projection": "proj_5070", "resolution": [r,r], \
                    "products": {"slope": "true", "hillshade": "true", \
                    "pitremove": "true"}, "resamplingMethod": \
                    "bilinear",
                    "fileFormat": "GTiff"}}
            js_lists.append(js_up)

        if "State" in set and len(nameWOSuffix)<3:
            comp = "proj_"+states[nameWOSuffix]
            js_up = {"visible": "true", "title": title, "public": \
                    "true", \
                    "input": {"source": source, "boundary": boundary, \
                    "projection": comp, "resolution": [r,r], \
                    "products": {"slope": "true", "hillshade": "true", \
                    "pitremove": "false"}, "resamplingMethod": \
                    "bilinear",
                    "fileFormat": "GTiff"}}
            js_lists.append(js_up)


# --------------------------- Get the Sources --------------------------------
def generateSources(inputDir, output, secondInputDir=None):
    """
    Generates the sources.json file

    Parameters:
    -----------
    inputDir:       - The input directory [/gpfs_scratch/ned_data_boundaries/\
                                           HUC/HUC2/geojson/]
    output:         - Name of the output sources file
    secondInputDir: - Name of a second input directory
    """
    name = "NED 1/3 arc second resolution data"
    _id = "USGS_NED_DATA"
    detail = "Details of the data source that can be recognized by the Data Service"
    keywords = ["USGS NED"]
    js_up = {"_id": _id, "visible": "true", "name": name, "detail": detail, "keywords": keywords}
    with open(output, 'wb') as json_file:
        json.dump(js_up, json_file, indent=4)


# --------------------------- Get the Projections ----------------------------
def generateProjections(inputDir, output, secondInputDir=None):
    """
    Generates the projections.json file

    Parameters:
    -----------
    inputDir:       - The input directory [/gpfs_scratch/ned_data_boundaries/\
                                           HUC/HUC2/geojson/]
    output:         - Name of the output projection file
    secondInputDir: - Name of a second input directory
    """
    epsg = ["4269", "3857", "5070"]
    retProj = []
    dictState = {}
    dictState[epsg[0]] = epsg[0]
    dictState[epsg[1]] = epsg[1]
    dictState[epsg[2]] = epsg[2]

    # Get Projection for all States
    if secondInputDir:
        stateList = []
        for fn in os.listdir(secondInputDir):
            fullPath = os.path.join(secondInputDir, fn)
            nameWOSuffix = fn.split(".")[0]
            with fiona.open(fullPath) as src:
                for layer in src:
                    stateList.append(layer['properties']['NAME'])

        # Get EPSG for all States 
        with open("stateEpsg.csv", 'r') as csvfile:
            stEpReader = csv.reader(csvfile) 
            for row in stEpReader:
                for state in stateList:
                    if state in row[2]:
                        epsg.append(row[3])
                        dictState[row[3]] = state
                        break

    for p in epsg:
        retProj.append(returnProjJson(dictState[p], p))

    # Write out into json file
    with open(output, 'wb') as json_file:
        json.dump(retProj, json_file, indent=4)

def getProjContent(epsg):
    """
    Returns the content of epsg

    Parameters:
    -----------
    epsg:       - The epsg number [epsg:4269]
    """
    info = subprocess.check_output(["gdalsrsinfo", epsg])
    return info.split('OGC WKT :\n')[1].strip()

def returnProjJson(fn, epsg):
    """
    Returns the projection information required by the projections.json

    Parameters:
    -----------
    fn:         - The name of the file without the .geojson suffix
    epsg:       - The epsg number [4269]
    """
    id = "proj_" + fn
    content = getProjContent("epsg:" + epsg)
    name = content.split(',')[0].split('[')[1].strip('\"')
    keywords = [x.strip() for x in name.split('/')]
    js_up = {"_id": id, "visible": "true", "name": name, "epsg": epsg, \
             "content": content, "keywords": keywords}
    return js_up


def main():
    parser = argparse.ArgumentParser(
            usage = 'python %s inputDir -s secondInputDir boundaryOutput \
                     projectionOutput productsOutput sourcesOutput' % __file__,
                    formatter_class=argparse.RawDescriptionHelpFormatter,
                    description=__doc__)
    parser.add_argument("inputDir", type=str, 
            help = "input directory containing geojson files")
    parser.add_argument("-s", "--secondInputDir", type=str, 
            help = "second input directory containing geojson files")
    parser.add_argument("boundaryOutput", type=str, 
            help = "Name of the boundary output json file")
    parser.add_argument("projectionOutput", type=str, 
            help = "Name of the projection output json file")
    parser.add_argument("productOutput", type=str, 
            help = "Name of the product output json file")
    parser.add_argument("sourcesOutput", type=str, 
            help = "Name of the sources output json file")
    args = parser.parse_args()

#    generateBoundaries(args.inputDir, args.boundaryOutput, \
#                               args.secondInputDir)
#    generateProjections(args.inputDir, args.projectionOutput, \
#                        args.secondInputDir)
#    generateProducts(args.inputDir, args.productOutput, args.secondInputDir)
#    generateSources(args.inputDir, args.sourcesOutput, args.secondInputDir)


if __name__ == "__main__":
    main()
