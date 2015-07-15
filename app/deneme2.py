#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wikitools import wiki, category, api, page
from bs4 import BeautifulSoup
import locale, datetime, sys, timestring
from models import Content

reload(sys)
sys.setdefaultencoding("UTF-8")
locale.setlocale(locale.LC_ALL, ('tr_TR', 'UTF-8'))

site = wiki.Wiki("https://tr.wikipedia.org/w/api.php")
password = raw_input("Sifrenizi giriniz:")
site.login("Yaslient1", password)


title_name = "Template:Location map Romania"

cont = page.Page(site, "Template:Location map Romania")
text = cont.getWikiText()




#print BeautifulSoup(text, 'html.parser').find("noinclude")


params = {
    'action': "edit",
    'title':'Kullanıcı:Yaslient',
    'bot': '1',
    'title': "Deneme123",
    #'token': site.getToken("csrf"),

}



a = Content(cont.getWikiText())
dict = a._getTemplate("#switch:{{{1}}}", text)
print a._templateToString("#switch:{{{1}}}", dict)




#a.render()
#a.fixBirthAndDeathDates()

#cont.edit(text=a.render())
