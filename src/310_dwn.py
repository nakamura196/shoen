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

print("start")

geo = requests.get("https://script.google.com/macros/s/AKfycbwYfhKrM3A8WZJhWOP6WDoNqxNeCqqoz-agemlDtdWIm5V5G6XsHEXAt9bnZZveqM6_/exec?sheet=all").json()

print(len(geo))

f2 = open("data/data.json", 'w')
json.dump(geo, f2, ensure_ascii=False, indent=4,
        sort_keys=True, separators=(',', ': '))