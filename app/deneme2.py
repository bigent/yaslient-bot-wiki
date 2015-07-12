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
site.login("Yaslient", "lotr123")

cont = page.Page(site, "Kullanıcı:Yaslient")
print cont.getWikiText()

params = {
    'action': "edit",
    'title':'Kullanıcı:Yaslient',
    'bot': '1',
    'title': "Deneme123",
    'token': site.getToken("csrf"),

}

a = Content(cont.getWikiText())




#a.render()
a.fixBirthAndDeathDates()

cont.edit(text=a.render())
