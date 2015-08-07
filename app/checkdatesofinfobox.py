#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wikitools import wiki, category, api, page
from models import Content
import sys, locale, getpass

reload(sys)
sys.setdefaultencoding("UTF-8")
locale.setlocale(locale.LC_ALL, ('tr_TR', 'UTF-8'))

site = wiki.Wiki("https://tr.wikipedia.org/w/api.php")
password = getpass.getpass("Sifrenizi giriniz:")
site.login("Yaslient1", password)

f1 = open("/home/bigent/Projects/yaslient-bot-wiki/data/dateinfobox_list.txt", "r")
data = []

for i in f1.readlines():
    i = str(i).strip()
    data.append(i)

for i in data:
    if not u"anon" in page.Page(site, title=i).getHistory()[0].keys():
        print "{} adlı maddenın wikitext'i alınıyor...".format(i)
        old_content = page.Page(site, title=i).getWikiText()
        print "Alındı."

        con = Content(content=old_content)
        old_infoboxes = con.findInfoboxes()
        print "Doğum ve ölüm tarihi yenileniyor..."
        con.fixBirthAndDeathDates()
        print "Yenilendi."

        if old_infoboxes == con.infoboxes:
            print "Herhangi bir değişiklik olmadığından madde düzenlenmiyor."
        else:
            print "Maddenin eski hali yeni haliyle değiştiriliyor..."
            page.Page(site, i).edit(con.render(), bot="yes", skipmd5=True)
            print "Değiştirildi."
        #print "====!===="
        #print con.render()
        #print "====!===="
        print "============"
print "İşlemler bitti."
