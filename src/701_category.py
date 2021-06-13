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
import glob
import bs4

from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace

soup = bs4.BeautifulSoup(requests.get("https://wwwap.hi.u-tokyo.ac.jp/ships_htdocs/ASSIST/W23/index.html").content, 'html.parser')

path = "data/category/index.html"

all = Graph()

if not os.path.exists:

  with open(path, mode='w') as f:
    f.write(str(soup))

for i in range(15):
  url = "https://wwwap.hi.u-tokyo.ac.jp/ships_htdocs/ASSIST/W23/"+str(i+1).zfill(2)+".html"

  opath = "data/category/"+url.split("/")[-1]

  if not os.path.exists(opath):

    soup = bs4.BeautifulSoup(requests.get(url).content, 'html.parser')

    with open(opath, mode='w') as f:
      f.write(str(soup))

  soup = bs4.BeautifulSoup(open(opath), 'html.parser')

  lev1 = soup.find("span").text
  print(lev1)

  subject = URIRef("https://jpsearch.go.jp/term/keyword/"+lev1)

  stmt = (subject, RDF.type, URIRef("https://jpsearch.go.jp/term/type/Keyword"))
  all.add(stmt)

  stmt = (subject, RDFS.label, Literal(lev1))
  all.add(stmt)

  trs = soup.find_all("tr")

  for tr in trs:
    lev2 = str(tr.find_all("td")[1].text)
    print(lev2)

    subject2 = URIRef("https://jpsearch.go.jp/term/keyword/"+lev2)

    stmt = (subject2, RDF.type, URIRef("https://jpsearch.go.jp/term/type/Keyword"))
    all.add(stmt)

    stmt = (subject2, RDFS.label, Literal(lev2))
    all.add(stmt)

    stmt = (subject2, URIRef("http://schema.org/"+"isPartOf"), subject)
    all.add(stmt)

  

path = "data/category.json"
all.serialize(destination=path, format='json-ld')
all.serialize(destination=path.replace(".json", ".ttl"), format='turtle')