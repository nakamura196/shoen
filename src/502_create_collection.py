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

files = glob.glob("../docs/iiif/*/manifest.json")

files = sorted(files)

f = open("../settings.yml", "r+")
prefix = yaml.load(f, Loader=yaml.SafeLoader)["prefix"]

manifests = []

for file in files:

    print(file)

    if "-" in file:
      continue

    json_open = open(file, 'r')
    manifest = json.load(json_open)

    manifests.append({
      "@type": "sc:Manifest",
      "@id": manifest["@id"],
      "label": manifest["label"],
      "thumbnail": manifest["thumbnail"]
    })

collection = {
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": prefix + "/collection/top.json",
    "@type": "sc:Collection",
    "label": "史料編纂所所蔵荘園絵図摸本データベース",
    "vhint": "use-thumb",
    "manifests": manifests
}

opath = "../docs/collection/top.json"
os.makedirs(os.path.dirname(opath), exist_ok=True)

f2 = open(opath, 'w')
json.dump(collection, f2, ensure_ascii=False, indent=4,
            sort_keys=True, separators=(',', ': '))