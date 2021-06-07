import urllib.request
from bs4 import BeautifulSoup
import csv
from time import sleep
import pandas as pd
import json
import urllib.request
import os
from PIL import Image
import yaml
import requests
import sys
import argparse

import utils

from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace

f = open("../settings.yml", "r+")
prefix = yaml.load(f, Loader=yaml.SafeLoader)["prefix"]

import re

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def handleManifest(cn, manifest):
    opath = "item/{}/manifest.json".format(cn)
    opath_anno = "item/{}/annolist.json".format(cn)

    if not os.path.exists(opath):

        m = requests.get(manifest).json()

        f2 = open(opath, 'w')
        json.dump(m, f2, ensure_ascii=False, indent=4,
                sort_keys=True, separators=(',', ': '))

        canvases = m["sequences"][0]["canvases"]

        for c in canvases:
            anno = c["otherContent"][0]["@id"]
            

            a = requests.get(anno).json()
            f2 = open(opath_anno, 'w')
            json.dump(a, f2, ensure_ascii=False, indent=4,
                sort_keys=True, separators=(',', ': '))

    json_open = open(opath_anno, 'r')
    annolist = json.load(json_open)

    resources = annolist["resources"]

    annos = {}

    for r in resources:
        annos[cleanhtml(r["resource"][0]["chars"])] = r["on"][0]["selector"]["default"]["value"].split("=")[1]

    return annos


f = open("../settings.yml", "r+")
prefix = yaml.load(f, Loader=yaml.SafeLoader)["prefix"]

cn = "仁-108"

settings2 = yaml.load(open("item/{}/settings.yml".format(cn), "r+"), Loader=yaml.SafeLoader)

print(settings2)

manifest = settings2["manifest"]

annos = handleManifest(cn, manifest)

print(annos)

df = pd.read_excel("item/{}/place.xlsx".format(cn), sheet_name=0, header=None, index_col=None, engine='openpyxl')

print(df)

r_count = len(df.index)
c_count = len(df.columns)

print("aaaaaa", r_count, c_count)

# uri	rdfs:label	description:推定した国郡名等	schema:description	schema:longitude	schema:latitude	schema:geo^^uri	xywh	schema:url	canvas	schema:relatedLink	schema:isPartOf^^uri
rows = []
rows.append(["uri", "dcterms:identifier", "ID", "description:架番号", "rdfs:label", "description:推定した国郡名等", "schema:description", "schema:longitude", "schema:latitude", "schema:geo^^uri", "xywh", "schema:url", "canvas", "schema:relatedLink", "schema:isPartOf^^uri"])

for i in range(1, r_count):

    print(i)

    cn2 = df.iloc[i, 12] + "-" + df.iloc[i, 13]

    label = df.iloc[i, 17]
    assume = df.iloc[i, 18]
    exp = df.iloc[i, 19]
    kml = df.iloc[i, 20]
    
    text = kml.split("<coordinates>")[1].split(",0</coordinates>")[0].split(",")
    lat = text[1]
    long = text[0]

    print(lat, long)

    id = cn2+"_"+label

    canvas = "https://lab-hi.github.io/map/iiif/1/manifest.json/canvas/p1"

    

    if label not in annos:
        xywh = ""
        member = ""
    else:
        xywh = annos[label]
        member = canvas + "#xywh=" + xywh

    rows.append(["http://example.org/data/"+id, id, "", cn2, label, assume, exp, long, lat, "", xywh, prefix + "/iiif/" + cn + "/manifest.json", canvas, member, "http://example.org/data/"+cn])


with open("item/{}/data.csv".format(cn), 'w') as f:
    writer = csv.writer(f)
    writer.writerows(rows)