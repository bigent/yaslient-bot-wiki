#!/usr/bin/python
# -*- coding: utf-8 -*-
from models import Content
from wikitools import api, wiki

import sys
sys.setdefaultencoding("utf-8")


site = wiki.Wiki("https://tr.wikipedia.org/w/api.php")
password = raw_input("Sifrenizi giriniz:")
site.login("Yaslient1", password)


params = {'action':'query',
    "prop": "revisions",
    "rvprop": "content",
#    "format": "json",
    "titles": "Stanley Matthews",

}
req = api.APIRequest(site, params)

#print req.query(querycontinue=False)["query"]["pages"]
content = req.query(querycontinue=False)["query"]["pages"]["1123232"]['revisions'][0]["*"].encode("utf-8")

a = Content(content=content)

#print a._getTemplate("Futbolcu bilgi kutusu", content)
#print(a._fixBirthDate(a.findInfoboxes()["Futbolcu bilgi kutusu"]))
#print(a._fixDeathDate(a.findInfoboxes()["Futbolcu bilgi kutusu"]))
a.render(a.findInfoboxes())
