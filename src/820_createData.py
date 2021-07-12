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
import glob

files = glob.glob("item/*/data.csv")

items = []

items.append({
        "label": "セット",
        "value": [
            {
                "dcterms:identifier": "W23",
                "rdfs:label": "史料編纂所所蔵荘園絵図摸本データベース",
                "uri": "http://example.org/data/W23"
            },
            {
                "dcterms:identifier": "W11",
                "rdfs:label": "鎌倉遺文フルテキストデータベース",
                "uri": "http://example.org/data/W11"
            }
        ]
    })

rows = []

items.append({
        "label": "まとめ",
        "value": rows})

for file in files:

    m_path = file.replace("data.csv", "manifest.json")

    m = open(m_path, 'r')
    m = json.load(m)

    label = m["label"]

    ##########

    with open(file.replace("data.csv", "row.csv")) as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            rows.append({
                "": "",
                "dcterms:identifier": row[1],
                "description:curation": row[5],
                "description:本文": row[7],
                "jps:sourceInfo": row[9],
                "rdfs:label": row[2],
                "schema:image": row[3],
                "schema:spatial": row[8],
                "schema:temporal": row[6],
                "schema:url": row[4],
                "temporal:label": row[6],
                "uri": row[0]
            })




    ##########

    values = []

    with open(file) as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            print(row)

            values.append({
                "ID": row[2],
                "canvas": row[14],
                "dcterms:identifier": row[1],
                "description:表記": row[5],
                "description:架番号": row[3],
                "rdfs:label": row[4],
                "schema:category": row[6],
                "schema:description": row[8],
                "schema:geo^^uri": row[11],
                "schema:isPartOf^^uri": row[17],
                "schema:latitude": row[10],
                "schema:longitude": row[9],
                "schema:relatedLink": row[15],
                "schema:url": row[13],
                "schema:image": row[16],
                "uri": row[0],
                "xywh": row[12]
            })

    items.append({
        "label": label,
        "value" : values
    })

f2 = open("data/data2.json", 'w')
json.dump(items, f2, ensure_ascii=False, indent=4,
    sort_keys=True, separators=(',', ': '))

'''

m = open(opath, 'r')
m = json.load(m)


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

        

        print(manifest)
        print(requests.get(manifest))
        print(requests.get(manifest).content)

        m = requests.get(manifest).json()

        f2 = open(opath, 'w')
        json.dump(m, f2, ensure_ascii=False, indent=4,
                sort_keys=True, separators=(',', ': '))
        f2.close()

    m = open(opath, 'r')
    m = json.load(m)

    canvases = m["sequences"][0]["canvases"]

    image = ""

    resources = []

    for c in canvases:
        anno = c["otherContent"][0]["@id"]
        
        if image == "":
            image = c["images"][0]["resource"]["service"]["@id"]
        
        a = requests.get(anno).json()

        print(a)

        for r in a["resources"]:
            resources.append(r)

    f2 = open(opath_anno, 'w')
    json.dump({"resources": resources}, f2, ensure_ascii=False, indent=4,
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

print(image)

### 要修正
df = pd.read_excel("data/place.xlsx".format(cn), sheet_name=0, header=None, index_col=None, engine='openpyxl')

r_count = len(df.index)
c_count = len(df.columns)

rows = []
rows.append(["uri", "dcterms:identifier", "ID", "description:架番号", "rdfs:label", "description:表記","schema:category","description:推定した国郡名等", "schema:description", "schema:longitude", "schema:latitude", "schema:geo^^uri", "xywh", "schema:url", "canvas", "schema:relatedLink", "schema:image", "schema:isPartOf^^uri"])

map_ = {}

for i in range(1, r_count):

    cn2 = "{}-{}".format(df.iloc[i, 12],df.iloc[i, 13])

    if not pd.isnull(df.iloc[i, 14]):
        cn2  = "{}-{}".format(cn2, df.iloc[i, 14])

    if cn2 != cn:
        continue

    label = df.iloc[i, 17]

    map_[label] = {
        "index": i,
        "value": df
    }

hash_id = hashlib.md5(cn.encode()).hexdigest()

manifest = prefix + "/iiif/" + hash_id + "/manifest.json"

print("len(annos)", len(annos))

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
    
    rows.append(["http://example.org/data/"+id, id, "", cn2, key, desc, category, assume, exp, long, lat, geohash, xywh, manifest, canvas, member, thumbnail, "http://example.org/data/"+cn])

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
'''