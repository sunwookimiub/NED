"""
Accept a directory as input and generate preset files for NED data.
"""
import os
import re
import json
import argparse
import fiona


def checkIfRelevant(set, nameWOSuffix):
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


def generateBoundaries(inputDir, output):
    count = 0
    js_lists = []
    set = inputDir.split("/")[4]
    for fn in os.listdir(inputDir):
        count = count + 1
        fullPath = os.path.join(inputDir,fn)
        nameWOSuffix = fn.split(".")[0] # Name of file without suffix
        if checkIfRelevant(set, nameWOSuffix):
            with fiona.open(fullPath, 'r') as src:
                for layer in src:
                    id = "{}_boundary_{}".format(set, str(count))
                    name = "{}_{}".format(set, nameWOSuffix)
                    prop = layer['properties']
                    desc = "{}. States = {}. Area (sqkm) = {}".format(\
                            prop['NAME'], prop['STATES'], prop['AREASQKM'])
                    with open(fullPath, 'r') as test:
                        shape = "'" + str(json.load(test)) + "'"
                    keywords = []
                    keywords.append(set)
                    js_up = {"_id": id, "visible": "true", "name": name,\
                              "description": desc, "projection": "EPSG:4269",\
                              "shape": shape, "keywords": keywords}
                    js_lists.append(js_up)

    with open(output, 'wb') as json_file:
        json.dump(js_lists, json_file, indent=4)


def findBoundaryID(boundaryFile, title):
    with open(boundaryFile, 'r') as b_file:
        data = json.load(b_file)
        for i in range(len(data)):
            if data[i]['name'] == title:
                return data[i]['_id']


def generateProducts(inputDir, output, boundaryFile):
    set = inputDir.split("/")[4]
    source = set
    projection = set + "_projection"
    r = 1.0/(360*3)
    js_lists = []
    for fn in os.listdir(inputDir):
        nameWOSuffix = fn.split(".")[0]
        title = set + "_" + nameWOSuffix
        boundary = findBoundaryID(boundaryFile, title)
        if boundary != None:
            js_up = {"visible": "true", "title": title, "public": "true", \
                     "input": {"source": source, "boundary": boundary, \
                     "projection": projection, "resolution": [r,r], \
                     "products": {"slope": "true", "hillshade": "true", \
                     "pitremove": "true"}, "resamplingMethod": "bilinear", \
                     "fileFormat": "GTiff"}}
            js_lists.append(js_up)

    with open(output, 'wb') as json_file:
        json.dump(js_lists, json_file, indent=4)


def generateProjections(inputDir, output):
    set = inputDir.split("/")[4]
    id = set + "_projection"
    name = "NAD83"
    epsg = "4269"
    content = "GEOGCS[\"NAD83\",\n\tDATUM[\"North_American_Datum_1983\",\n \
               \t\tSPHEROID[\"GRS 1980\",6378137,298.257222101,\n\t\t\t \
               AUTHORITY[\"EPSG\",\"7019\"]],\n\t\tAUTHORITY[\"EPSG\",\"6269\
               \"]],\n\tPRIMEM[\"Greenwich\",0,\n\t\tAUTHORITY[\"EPSG\",\"\
               8901\"]],\n\tUNIT[\"degree\",0.01745329251994328,\n\t\t \
               AUTHORITY[\"EPSG\",\"9122\"]],\n\tAUTHORITY[\"EPSG\",\"4269\"]]"
    keywords = re.sub('[0-9]',' ',name.replace(" ","")).lower().split()
    js_up = {"_id": id, "visible": "true", "name": name, "epsg": epsg, \
             "content": content, "keywords": keywords}
    with open(output, 'wb') as json_file:
        json.dump(js_up, json_file, indent=4)


def main():
    parser = argparse.ArgumentParser(
            usage = 'python %s inputDir boundaryOutput projectionOutput\
                    productsOutput'\
                     % __file__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=__doc__)
    parser.add_argument("inputDir", type=str, 
            help = "input directory containing geojson files")
    parser.add_argument("boundaryOutput", type=str, 
            help = "Name of the boundary output json file")
    parser.add_argument("projectionOutput", type=str, 
            help = "Name of the projection output json file")
    parser.add_argument("productOutput", type=str, 
            help = "Name of the product output json file")
    args = parser.parse_args()
    generateBoundaries(args.inputDir, args.boundaryOutput)
    generateProjections(args.inputDir, args.projectionOutput)
    generateProducts(args.inputDir, args.productOutput, args.boundaryOutput)


if __name__ == "__main__":
    main()
