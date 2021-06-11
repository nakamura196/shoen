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

from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace

f = open("../settings.yml", "r+")
config = yaml.load(f, Loader=yaml.SafeLoader)
app = config["app"]
prefix = config["prefix"]

# all = Graph()

###########

json_open = open("data/data.json", 'r')
geo = json.load(json_open)

map = {}

colors = {
    "寺" : "#F44336",
    "山" : "#9C27B0",
    "川" : "#009688",
    "堂" : "#8BC34A",
    "池" : "#FF9800",
    "宮" : "#795548",
}

for sheet in geo:

    if sheet["label"] in ["セット", "まとめ"]:
        continue

    rows = sheet["value"]

    print(sheet["label"])
    for row in rows:
        

        if "uri" not in row and row["uri"] == "":
            continue

        print(row["uri"])

        manifest = row["schema:url"]

        if manifest not in map:
            map[manifest] = {
                "members": [],
                "label" : "", # row["parent:label"],
                "uri": row["schema:isPartOf^^uri"]
            }

        member_id = row["schema:relatedLink"]
        id = row["dcterms:identifier"]
        url = app + "/item/" + id

        print(id)

        label = row["rdfs:label"]

        tag = row["schema:category"] if "schema:category" in row else ""

        tag_str = ""

        if tag != "":

            tag_str = "<br/>分類："+tag

        color = "#2196F3"

        if tag in colors:
            color = colors[tag]

        member = {

            "@id": member_id,
            "@type": "sc:Canvas",
            "label": label,
            "metadata": [
                {
                    "label": "Annotation",
                    "value": [
                        {
                            "@id": url,
                            "@type": "oa:Annotation",
                            "motivation": "sc:painting",
                            "on": member_id,
                            "resource": {
                                "@type": "cnt:ContentAsText",
                                "chars": '''[ <a href=\"{}\">{}</a> ]<br/>地名：{}{}'''.format(url, id, label, tag_str),
                                "format": "text/html",
                                "marker": {
                                "@id": "https://cdn.mapmarker.io/api/v1/pin?size=25&background=%23"+color.replace("#", "")+"&color=%23FFFFFF&voffset=0&hoffset=1&icon=fa-circle#xy=12,22",
                                "@type": "dctypes:Image"
                                }
                            }
                        }
                    ]
                }
            ]

        }

        map[manifest]["members"].append(member)



for manifest in map:
    selections = []
    
    print(manifest)
    item = map[manifest]

    print(len(item["members"]))

    label = item["label"]
    selections.append({
        "@id": manifest + "/range",
        "@type": "sc:Range",
        "label": label,
        "members": item["members"],
        "within": {
            "@id": manifest,
            "@type": "sc:Manifest",
            "label": label
        }
    })

    id = item["uri"].split("/")[-1]

    curation = {
        "@context": [
            "http://iiif.io/api/presentation/2/context.json",
            "http://codh.rois.ac.jp/iiif/curation/1/context.json"
        ],
        "@id": prefix + "/curation/" + id + ".json",
        "@type": "cr:Curation",
        "label": label,
        "selections": selections,
        "viewingHint": "annotation"
    }

    f2 = open("../docs/curation/"+id+".json", 'w')
    json.dump(curation, f2, ensure_ascii=False, indent=4,
            sort_keys=True, separators=(',', ': '))
