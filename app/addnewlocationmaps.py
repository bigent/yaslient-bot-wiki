#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wikitools import wiki, category, api, page
from models import Content
import sys, locale

reload(sys)
sys.setdefaultencoding("UTF-8")
locale.setlocale(locale.LC_ALL, ('tr_TR', 'UTF-8'))

f1 = open("/home/bigent/Projects/yaslient-bot-wiki/data/trans_list.txt", "r")
data = []
for i in f1.readlines():
    i = str(i).strip()
    org_name = str(i).split("-->")[0]
    try:
        name = str(i).split("-->")[1].split("?*?")[0]
    except:
        break
    if len(str(i).split("-->")[1].split("?*?")) > 1:
        try:
            categories = str(i).split("-->")[1].split("?*?")[1].split("?")
        except:
            categories = [str(i).split("-->")[1].split("?*?")[0]]
    else:
        categories = ""
    data.append( {"org_name": org_name, "name": name, "categories": categories} )
print("Datalar ayıklandı.")
f1.close()

site = wiki.Wiki("https://tr.wikipedia.org/w/api.php")
password = raw_input("Sifrenizi giriniz:")
site.login("Yaslient1", password)

for locationmap in data:
    org_name, name, categories = locationmap["org_name"], locationmap["name"], locationmap["categories"]
    try:
        site = wiki.Wiki("https://tr.wikipedia.org/w/api.php")
        site.login("Yaslient1", password)
        page.Page(site, "Şablon:{} konum haritası".format(name) ).getWikiText()
        print "Hata: {} adında bir bir şablon var. Bu yüzden bu şablon atlandı.".format(name)
        pass
    except:
        site = wiki.Wiki("https://en.wikipedia.org/w/api.php")
        site.login("Yaslient1", password)

        enTemplateContent = page.Page(site, "Template:Location map {}".format(org_name) )
        enTemplateContent.setPageInfo
        print "İngilizce Vikipedi'den {} adlı şablonun verileri alınıyor...".format(org_name)
        enTemplate = Content(enTemplateContent.getWikiText())
        print "Alındı."
        enDict = enTemplate._getTemplate("#switch:{{{1}}}", enTemplate._content)
        enDict["name"] = name

        print "Türkçe Vikipedi için şablon hazırlanıyor..."
        trTemplateContent = enTemplate._templateToString("#switch:{{{1}}}", enDict)
        print "Hazırlandı."

        trTemplateContent += "<noinclude>"
        if categories:
            site = wiki.Wiki("https://tr.wikipedia.org/w/api.php")
            site.login("Yaslient1", password)
            for theCategory in categories:
                try:
                    page.Page(site, "Kategori:{} konum haritası şablonları".format(theCategory) ).getWikiText()
                except:
                    #Yeni kategori oluştur!
                    params = {
                        'action': "edit",
                        'title': "Kategori:{} konum haritası şablonları".format(theCategory),
                        'text': "[[Kategori:Ülkelerine göre harita şablonları]]",
                        'section': 'new',
                        #'summary': '',#'Böyle bir kategori bulunamadığından eklendi.',
                        'bot':'true',
                        'token': site.getToken("csrf"),
                    }
                    print "Yeni kategori ekleniyor..."
                    asd = api.APIRequest(site, params)
                    asd.query(False)
                    print "Yeni kategori eklendi."

                #Content'e kategoriyi ekle!
                print "Şablona {} adlı kategori ekleniyor".format(theCategory)
                trTemplateContent += "[[Kategori:{} konum haritası şablonları]]".format(theCategory)
                print "Eklendi."
        else:
            trTemplateContent += "[[Kategori:Harita konum şablonları]]"
            print "Herhangi bir kategori olmadığından varsayılan kategoriye eklendi."

        trTemplateContent += "{{Konum haritası/Bilgi}}</noinclude>"
        print "Şablon tamamlandı."

        site = wiki.Wiki("https://tr.wikipedia.org/w/api.php")
        site.login("Yaslient1", password)

        params = {
            'action': "edit",
            'title': "Şablon:{} konum haritası".format(name),
            'text': trTemplateContent,
            'section': 'new',
            #'summary': '',#"İngilizce Vikipedi'den konum şablonları aktarılıyor.",
            'bot':'true',
            'token': site.getToken("csrf"),
        }
        print "{} adlı şablon Türkçe Vikipedi'ye ekleniyor...".format(name)
        asd = api.APIRequest(site, params)
        asd.query(False)
        print "Başarıyla eklenildi."

        params = {
            'action': "wbgetentities",
            'sites': 'enwiki',
            'titles': "Template:Location map {}".format(org_name),
            'props': 'labels',
            'format': 'json'
        }
        site = wiki.Wiki("https://www.wikidata.org/w/api.php")
        site.login("Yaslient1", password)
        req = api.APIRequest(site, params)
        for i in req.query(querycontinue=False)["entities"].iterkeys():
            print "Interwiki'ye ekleniyor..."
            params = {
                'action': "wbeditentity",
                'id': i,
                "data": '{"sitelinks":[{"site":"trwiki","title":"Şablon:'+name+' konum haritası","add":""}]}',
                "format": "jsonfm",
                'token': site.getToken("csrf"),
            }
            asd = api.APIRequest(site, params)
            try:
                asd.query()
            except:
                pass
            print "Eklenildi."
            break

print "İşlemler başarıyla bitti."
