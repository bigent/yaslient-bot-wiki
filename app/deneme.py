#!/usr/bin/python
# -*- coding: utf-8 -*-
from models import Content
from wikitools import api, wiki, page
import sys, getpass
sys.setdefaultencoding("utf-8")


site = wiki.Wiki("https://tr.wikipedia.org/w/api.php")
password = getpass.getpass("Sifrenizi giriniz:")
site.login("Yaslient1", password)

print page.Page(site, title="Sadettin Kaynak").getHistory()
#eğer anon varsa pas get ve kaydet
pass
params = {'action':'query',
    #"prop": "revisions",
    "rvprop": "content",
#    "format": "json",
    "titles": "Sadettin Kaynak",

}
req = api.APIRequest(site, params)

#print req.query(querycontinue=False)["query"]["pages"]
#content = req.query(querycontinue=False)["query"]["pages"]["1123232"]['revisions'][0]["*"].encode("utf-8")
#print req.query(querycontinue=False)["query"]["pages"].items()[0][1]['revisions'][0]["*"].encode("utf-8")
print req.query(querycontinue=False)["query"]["pages"]
#a = Content(content=content)

#print a._getTemplate("Futbolcu bilgi kutusu", content)
#print(a._fixBirthDate(a.findInfoboxes()["Futbolcu bilgi kutusu"]))
#print(a._fixDeathDate(a.findInfoboxes()["Futbolcu bilgi kutusu"]))
#a.render(a.findInfoboxes())
