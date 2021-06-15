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
import hashlib
import utils
import geohash2
from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace

import argparse    # 1. argparseをインポート

parser = argparse.ArgumentParser(description='このプログラムの説明（なくてもよい）')    # 2. パーサを作る

# 3. parser.add_argumentで受け取る引数を追加していく
parser.add_argument('label', help='この引数の説明（なくてもよい）') 

args = parser.parse_args()    # 4. 引数を解析



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
        f2.close()

    m = open(opath, 'r')
    m = json.load(m)

    canvases = m["sequences"][0]["canvases"]

    image = ""

    for c in canvases:
        anno = c["otherContent"][0]["@id"]
        
        if image == "":
            image = c["images"][0]["resource"]["service"]["@id"]

        a = requests.get(anno).json()
        f2 = open(opath_anno, 'w')
        json.dump(a, f2, ensure_ascii=False, indent=4,
            sort_keys=True, separators=(',', ': '))
        f2.close()
    

    json_open = open(opath_anno, 'r')
    annolist = json.load(json_open)

    resources = annolist["resources"]

    annos = []

    for r in resources:
        obj = {
            "canvas": r["on"][0]["full"],
            "xywh": r["on"][0]["selector"]["default"]["value"].split("xywh=")[1]
        }
        for res in r["resource"]:
            type_ = res["@type"]
            value = cleanhtml(res["chars"]).replace("_", "　")
            if type_ == "dctypes:Text":
                obj["label"] = value.replace("&nbsp;", "")
            if type_ == "oa:Tag":
                if "loc:" in value:
                    obj["loc"] = value.replace("loc:", "")
                else:
                    obj["tag"] = value

            obj["key"] = obj["loc"] if "loc" in obj else obj["label"]

        annos.append(obj)

    return annos, image

cn = args.label

settings2 = yaml.load(open("item/{}/settings.yml".format(cn), "r+"), Loader=yaml.SafeLoader)

manifest = settings2["manifest"]

# image = settings2["image"]


annos, image = handleManifest(cn, manifest)

df = pd.read_excel("item/{}/place.xlsx".format(cn), sheet_name=0, header=None, index_col=None, engine='openpyxl')

r_count = len(df.index)
c_count = len(df.columns)

rows = []
rows.append(["uri", "dcterms:identifier", "ID", "description:架番号", "rdfs:label", "description:表記","schema:category","description:推定した国郡名等", "schema:description", "schema:longitude", "schema:latitude", "schema:geo^^uri", "xywh", "schema:url", "canvas", "schema:relatedLink", "schema:image", "schema:isPartOf^^uri"])

map_ = {}

for i in range(1, r_count):

    cn2 = df.iloc[i, 12] + "-" + df.iloc[i, 13]

    label = df.iloc[i, 17]

    map_[label] = {
        "index": i,
        "value": df
    }

for anno in annos:

    label = anno["label"]

    key = anno["key"]

    canvas = anno["canvas"]

    xywh = anno["xywh"]

    member = canvas + "#xywh=" + xywh

    category = anno["tag"] if "tag" in anno else ""

    if key in map_:
        obj = map_[key]
        i  = obj["index"]
        df = obj["value"]

        assume = df.iloc[i, 18]
        exp = df.iloc[i, 19]
        kml = df.iloc[i, 20]
        
        text = kml.split("<coordinates>")[1].split(",0</coordinates>")[0].split(",")
        lat = text[1]
        long = text[0]
        geohash = "http://geohash.org/" + (geohash2.encode(float(lat), float(long)))
    else:
        assume = ""
        exp = ""
        long = ""
        lat = ""
        geohash = ""

    id = hashlib.md5((cn + member).encode('utf-8')).hexdigest()

    cn2 = cn

    desc = label

    thumbnail = image + "/" + xywh + "/200,/0/default.jpg"
    
    rows.append(["http://example.org/data/"+id, id, "", cn2, key, desc, category, assume, exp, long, lat, geohash, xywh, prefix + "/iiif/" + cn + "/manifest.json", canvas, member, thumbnail, "http://example.org/data/"+cn])

with open("item/{}/data.csv".format(cn), 'w') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

parent = "http://example.org/data/W23"

with open("item/{}/row.csv".format(cn), 'w') as f:
    rows = []
    rows.append(["uri", "dcterms:identifier", "rdfs:label", "schema:image", "schema:url", "description:curation", "temporal:label", "schema:temporal", "description:本文", "schema:spatial", "jps:sourceInfo"])
    rows.append(["http://example.org/data/" + cn, cn, label, thumbnail, manifest, "https://nakamura196.github.io/soen/curation/"+cn+".json", "", "", "", "", parent])
    writer = csv.writer(f)
    writer.writerows(rows)