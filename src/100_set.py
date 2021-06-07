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

all = Graph()

###########

json_open = open("data/data.json", 'r')
geo = json.load(json_open)

for sheet in geo:
    name = sheet["label"]

    if name != "セット":
        continue

    rows = sheet["value"]

    for row in rows:
        if "uri" not in row or row["uri"] == "":
            continue

        print(row["uri"])
        subject = URIRef(row["uri"])

        stmt = (subject, RDFS.label, Literal(row["rdfs:label"]))
        all.add(stmt)

        stmt = (subject, RDF.type, URIRef("https://jpsearch.go.jp/term/type/Agent"))
        all.add(stmt)

        


path = "data/set.json"
all.serialize(destination=path, format='json-ld')
all.serialize(destination=path.replace(".json", ".ttl"), format='turtle')
