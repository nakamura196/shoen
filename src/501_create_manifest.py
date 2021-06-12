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

from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace

import argparse    # 1. argparseをインポート

parser = argparse.ArgumentParser(description='このプログラムの説明（なくてもよい）')    # 2. パーサを作る

# 3. parser.add_argumentで受け取る引数を追加していく
parser.add_argument('label', help='この引数の説明（なくてもよい）') 

args = parser.parse_args()    # 4. 引数を解析

cn = args.label

settings2 = yaml.load(open("item/{}/settings.yml".format(cn), "r+"), Loader=yaml.SafeLoader)


image = settings2["image"]



url = image

urls = [url]

pages = "https://nakamura196.github.io/shoen"

canvases = []
thumbnail = {}

label = cn

for i in range(len(urls)):

    index = i + 1

    image = urls[i]

    url = image + "/info.json"

    df = requests.get(url).json()

    width = df["width"]
    height = df["height"]

    canvases.append({
        "@id": "{pages}/iiif/{cn}/manifest.json/canvas/p{index}".format(pages=pages, cn=cn, index=index),
        "@type": "sc:Canvas",
        "height": height,
        "images": [
            {
                "@id": "{pages}/iiif/{cn}/manifest.json/annotation/p{index}-image".format(pages=pages, cn=cn, index=index),
                "@type": "oa:Annotation",
                "motivation": "sc:painting",
                "on": "{pages}/iiif/{cn}/manifest.json/canvas/p{index}".format(pages=pages, cn=cn, index=index),
                "resource": {
                    "@id": "{image}/full/full/0/default.jpg".format(image=image),
                    "@type": "dctypes:Image",
                    "format": "image/jpeg",
                    "height": height,
                    "service": {
                        "@context": "http://iiif.io/api/image/2/context.json",
                        "@id": "{image}".format(image=image),
                        "profile": "http://iiif.io/api/image/2/level1.json"
                    },
                    "width": width
                }
            }
        ],
        "label": "[{index}]".format(index=index),
        "thumbnail": {
            "@id": "{image}/full/200,/0/default.jpg".format(image=image)
        },
        "width": width
    })

manifest = {
    "@id": "{pages}/iiif/{cn}/manifest.json".format(pages=pages, cn=cn),
    "@type": "sc:Manifest",
    "attribution": "東京大学史料編纂所",
    "label": label,
    "license": "https://www.hi.u-tokyo.ac.jp/faq/reuse_cc-by.html",
    "related": "http://universalviewer.io/examples/uv/uv.html#?manifest={pages}/iiif/{cn}/manifest.json".format(pages=pages, cn=cn),
    "sequences": [
        {
            "@id": "{pages}/iiif/{cn}/manifest.json/sequence/normal".format(pages=pages, cn=cn),
            "@type": "sc:Sequence",
            "canvases": canvases,
            "label": "Current Page Order",
            "viewingHint": "non-paged"
        }
    ],
    "thumbnail": {
        "@id": "{image}/full/200,/0/default.jpg".format(image=urls[0])
    },
    "viewingDirection": "left-to-right"
}

opath = "../docs/iiif/" + cn + "/manifest.json"
os.makedirs(os.path.dirname(opath), exist_ok=True)

f2 = open(opath, 'w')
json.dump(manifest, f2, ensure_ascii=False, indent=4,
            sort_keys=True, separators=(',', ': '))