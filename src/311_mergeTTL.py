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

import glob

from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace

files = glob.glob("data/*.ttl", recursive=True)

all = Graph()

for file in files:

        if "merge.ttl" in file:
                continue


        g = Graph()
        g.parse(file, format='turtle')

        all += g

all.serialize("data/merge.ttl", format='turtle')