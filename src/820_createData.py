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