#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wikitools import wiki, category, api, page
from bs4 import BeautifulSoup
import locale, datetime, sys, timestring
from models import Content

reload(sys)
sys.setdefaultencoding("UTF-8")
locale.setlocale(locale.LC_ALL, ('tr_TR', 'UTF-8'))

site = wiki.Wiki("https://www.wikidata.org/w/api.php")
password = raw_input("Sifrenizi giriniz:")
site.login("Yaslient1", password)


title_name = "Template:Location map Romania"

#cont = page.Page(site, "Şablon:Uruguayas konum haritası")
#text = cont.getWikiText()




#print BeautifulSoup(text, 'html.parser').find("noinclude")


#params = {
#    'action': "edit",
#    'title':'Kullanıcı:Yaslient',
#    'bot': '1',
#    'title': "Deneme123",
#    #'token': site.getToken("csrf"),
#
#}

params = {
    'action': "wbeditentity",
    'id': 'Q16761608',
    "data": '{"sitelinks":[{"site":"trwiki","title":"Şablon:ABD Alabama konum haritası","add":""}]}',
    "format": "jsonfm",
    'token': site.getToken("csrf"),

}

req = api.APIRequest(site, params)
content = req.query(querycontinue=False)
print content
#a = Content(cont.getWikiText())
#dict = a._getTemplate("#switch:{{{1}}}", text)
#print a._templateToString("#switch:{{{1}}}", dict)




#a.render()
#a.fixBirthAndDeathDates()

#cont.edit(text=a.render())
