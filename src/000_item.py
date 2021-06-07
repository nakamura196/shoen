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

geo = requests.get("https://script.google.com/macros/s/AKfycbwYfhKrM3A8WZJhWOP6WDoNqxNeCqqoz-agemlDtdWIm5V5G6XsHEXAt9bnZZveqM6_/exec?sheet=all").json()

f2 = open("data/data.json", 'w')
json.dump(geo, f2, ensure_ascii=False, indent=4,
        sort_keys=True, separators=(',', ': '))

for sheet in geo:
    name = sheet["label"]

    if name != "まとめ":
        continue

    rows = sheet["value"]

    for row in rows:
        if "uri" not in row or row["uri"] == "":
            continue

        uri = row["uri"]

        print(uri)
        subject = URIRef(uri)

        stmt = (subject, RDFS.label, Literal(row["rdfs:label"]))
        all.add(stmt)

        stmt = (subject, RDF.type, URIRef("https://jpsearch.go.jp/term/type/Item"))
        all.add(stmt)

        for key in row:
            if "description:" in key:
                if row[key] == "":
                    continue
                ln = key.replace("description:", "").strip()
                stmt = (subject, URIRef("http://schema.org/description"), Literal(ln+": "+row[key]))
                all.add(stmt)
            elif "schema:description" in key:
                if row[key] == "":
                    continue
                stmt = (subject, RDFS.comment, Literal(row[key]))
                all.add(stmt)
            elif "schema:geo" in key:
                if row[key] == "":
                    continue
                geo = URIRef(row[key])
                stmt = (subject, URIRef("http://schema.org/geo"), geo)
                all.add(stmt)

                stmt = (geo, URIRef("http://schema.org/latitude"), Literal(float(row["schema:latitude"])))
                all.add(stmt)

                stmt = (geo, URIRef("http://schema.org/longitude"), Literal(float(row["schema:longitude"])))
                all.add(stmt)
            elif "schema:url" in key:
                if row[key] == "":
                    continue
                manifest = URIRef(row[key])
                stmt = (subject, URIRef("http://schema.org/url"), manifest)
                all.add(stmt)

                stmt = (manifest, RDF.type, URIRef("http://iiif.io/api/presentation/2#Manifest"))
                all.add(stmt)
            elif "schema:relatedLink" in key:
                stmt = (subject, URIRef("http://schema.org/relatedLink"), URIRef(row[key]))
                all.add(stmt)
            elif "schema:image" in key:
                stmt = (subject, URIRef("http://schema.org/image"), URIRef(row[key]))
                all.add(stmt)
            elif "schema:isPartOf" in key:
                parent = URIRef(row[key])
                stmt = (parent, URIRef("http://schema.org/spatial"), subject)
                all.add(stmt)

                stmt = (parent, RDFS.label, Literal(row["parent:label"]))
                all.add(stmt)

                parent_id = row[key].split("/")[-1]

                stmt = (subject, URIRef("https://jpsearch.go.jp/term/property#sourceData"), URIRef(prefix + "/curation/" + parent_id + ".json"))
                all.add(stmt)

            elif "schema:spatial" in key:
                if row[key] == "":
                    continue
                stmt = (subject, URIRef("http://schema.org/spatial"), URIRef(row[key]))
                all.add(stmt)

            elif "schema:temporal" in key:
                if row[key] == "":
                    continue

                temporal = URIRef(row[key])

                stmt = (subject, URIRef("http://schema.org/temporal"), temporal)
                all.add(stmt)

                stmt = (temporal, RDFS.label, Literal(row["temporal:label"]))
                all.add(stmt)

                stmt = (temporal, RDF.type, URIRef("https://jpsearch.go.jp/term/type/Time"))
                all.add(stmt)

            elif "jps:sourceInfo" in key:
                if row[key] == "":
                    continue

                source = URIRef(uri + "#sourceinfo")

                stmt = (subject, URIRef("https://jpsearch.go.jp/term/property#sourceInfo"), source)
                all.add(stmt)

                stmt = (source, URIRef("http://schema.org/provider"), URIRef(row[key]))
                all.add(stmt)

                stmt = (source, RDF.type, URIRef("https://jpsearch.go.jp/term/type/ソース情報"))
                all.add(stmt)


path = "data/item.json"
all.serialize(destination=path, format='json-ld')
all.serialize(destination=path.replace(".json", ".ttl"), format='turtle')
