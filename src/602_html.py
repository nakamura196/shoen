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

files = glob.glob("data/scr/html/*.html")

files = sorted(files)

pages = "https://nakamura196.github.io/shoen"

for file in files:

  print(file)

  count = file.split("/")[-1].split(".")[0]

  path = "data/scr/image/" + str(count).zfill(4)+".html"

  if not os.path.exists:

    soup = bs4.BeautifulSoup(open(file), 'html.parser')

    url = str(soup).split("openImageViewer('")[1].split("'")[0]

    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    with open(path, mode='w') as f:
        f.write(str(soup))

  metadata = bs4.BeautifulSoup(open(file), 'html.parser')

  trs = metadata.find_all("tr")

  ms = []

  cn = ""
  label = ""

  for tr in trs:
    tds = tr.find_all("td")

    if len(tds) == 1:
      continue

    field = tds[0].text
    value = tds[1].text

    if value == "":
      continue

    if "【架番号】" in field:
      cn = value

    elif "【名称】" in field:
      label = value

    elif "【" in field:
        ms.append({
          "label" : field.replace("【", "").replace("】", ""),
          "value" : value.strip()
        })

  soup = bs4.BeautifulSoup(open(path), 'html.parser')
  list2 = str(soup).split("var jsonUrls = [")[1].split("]")[0].replace("\"", "").split(",")

  prefix = str(soup).split("viewUrlRoot = '")[1].split("'")[0].replace("/view/", "/api/image/")

  canvases = []

  index = 0

  cn_hash = hashlib.md5(cn.encode()).hexdigest()

  for i in range(len(list2)):

    id = list2[i]

    if "." in id:
      continue

    index += 1

    image = prefix + id + ".tif"

    info = image + "/info.json"

    hash_id = hashlib.md5(info.encode()).hexdigest()

    file = "data/scr/hash/" + hash_id + ".json"

    if not os.path.exists(file):
      df = requests.get(info).json()

      f2 = open(file, 'w')
      json.dump(df, f2, ensure_ascii=False, indent=4,
                  sort_keys=True, separators=(',', ': '))


    json_open = open(file, 'r')
    df = json.load(json_open)

    width = df["width"]
    height = df["height"]
    

    canvases.append({
        "@id": "{pages}/iiif/{cn}/canvas/p{index}".format(pages=pages, cn=cn_hash, index=index),
        "@type": "sc:Canvas",
        "height": height,
        "images": [
            {
                "@id": "{pages}/iiif/{cn}/annotation/p{index}-image".format(pages=pages, cn=cn_hash, index=index),
                "@type": "oa:Annotation",
                "motivation": "sc:painting",
                "on": "{pages}/iiif/{cn}/canvas/p{index}".format(pages=pages, cn=cn_hash, index=index),
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
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": "{pages}/iiif/{cn}/manifest.json".format(pages=pages, cn=cn_hash),
    "@type": "sc:Manifest",
    "attribution": "東京大学史料編纂所",
    "metadata": ms,
    "label": label,
    "license": "https://www.hi.u-tokyo.ac.jp/faq/reuse_cc-by.html",
    "related": "http://universalviewer.io/examples/uv/uv.html#?manifest={pages}/iiif/{cn}/manifest.json".format(pages=pages, cn=cn_hash),
    "sequences": [
        {
            "@id": "{pages}/iiif/{cn}/sequence/normal".format(pages=pages, cn=cn_hash),
            "@type": "sc:Sequence",
            "canvases": canvases,
            "label": "Current Page Order",
            "viewingHint": "non-paged"
        }
    ],
    "thumbnail": {
        "@id": "{image}/full/200,/0/default.jpg".format(image=prefix + list2[0] + ".tif")
    },
    "viewingDirection": "left-to-right"
  }

  opath = "../docs/iiif/" + cn_hash + "/manifest.json"
  os.makedirs(os.path.dirname(opath), exist_ok=True)

  f2 = open(opath, 'w')
  json.dump(manifest, f2, ensure_ascii=False, indent=4,
              sort_keys=True, separators=(',', ': '))