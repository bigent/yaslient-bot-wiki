#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wikitools import wiki, category, api, page
from bs4 import BeautifulSoup
import locale, datetime, sys, timestring, re

reload(sys)
sys.setdefaultencoding("UTF-8")
locale.setlocale(locale.LC_ALL, ('tr_TR', 'UTF-8'))

site = wiki.Wiki("https://tr.wikipedia.org/w/api.php")



class Content(object):
    def __init__(self, content):
        self._content = content.encode("utf-8")
        self.infoboxes = self.findInfoboxes()

    @staticmethod
    def _getStartEndIndexOfTemplate(infobox_name, content):
        input = content
        length = len(input)
        startIndex = input.lower().find("{{" + infobox_name.lower()) + 2 + len(infobox_name)
        braces = 0
        for i in range(startIndex, length):
            c = input[i]
            if (c == "{"):
                braces += 1
            elif (c == "}" and braces > 0):
                braces -= 1
            elif (c == "["):
                braces += 1
            elif (c == "]" and braces > 0):
                braces -= 1
            elif (c == "<" and input[i+1] == "!"):
                braces += 1
            elif (c == ">" and braces > 0 and input[i-1] == "-"):
                braces -= 1
            elif (c == "}" and braces == 0):
                endIndex = i
        return [startIndex-2-len(infobox_name), endIndex+1]

    def _getTemplate(self, name, content):
        input = content
        startIndex = input.lower().find("{{" + name.lower()) + 2 + len(name)
        length = len(input)
        braces = 0
        result = ""
        last_char = ""
        for i in range(startIndex, length):
            c = input[i]
            if (c == "{"):
                braces += 1
                last_char = c
            elif (c == "}" and braces > 0):
                braces -= 1
                last_char = c
            elif (c == "["):
                braces += 1
                last_char = c
            elif (c == "]" and braces > 0):
                braces -= 1
                last_char = c
            elif (c == "<" and input[i+1] == "!"):
                braces += 1
                last_char = c
            elif (c == "<" and input[i+1] != "!"):
                last_char = c
            elif (c == ">" and braces > 0 and input[i-1] == "-"):
                braces -= 1
                last_char = c
            elif (c == "}" and braces == 0):
                result = result.strip()
                parts = result.split("|")
                dict = {}
                counter = 0
                for part in parts:
                    part = part.strip()
                    kv = part.split("=")
                    key = kv[0].strip()
                    if (len(key) > 0):
                        val = ""
                        if (len(kv) > 1):
                            val = kv[1].strip().replace("%!%!%", "|").replace("%@%@%", "=")
                        else:
                            val = key;
                            key = counter
                            counter += 1
                        dict[key] = val
                return dict
            elif (c == "|" and braces > 0):
                last_char = c
                c = "%!%!%"
            elif (c == "=" and braces > 0) or (c == "=" and input[i+1] in ('"', '"') and last_char == "<"):
                last_char = c
                c = "%@%@%"
            result += c

    def _findInfoboxesName(self):
        content = self._content
        templates = [
        "Kişi bilgi kutusu şablonları",
        "Futbol bilgi kutusu şablonları",
        "Sanat bilgi kutusu şablonları",
        "Askeri bilgi kutusu şablonları",
        "Sporcu bilgi kutusu şablonları‎"
        ]
        list = []

        for template in templates:
            data = category.Category(site, template).getAllMembers(True)
            for i in data:
                i = i[7:]
                try:
                    if content.find(i) != -1 and str(i).endswith("bilgi kutusu"):
                        self._getTemplate(i, content)
                        list.append(i)
                except:
                    pass
                #if i in content.strip():
                #    print content.strip()[:content.strip().find(i)+1]
                #    print content.strip()[:content.strip().find(i)+2]
                #if ( i in content.strip() ) and content.strip()[:content.strip().find(i)+1].endswith("{"):


        return list

    def findInfoboxes(self):
        boxes = self._findInfoboxesName()
        dict = {}

        for box in boxes:
            dict[str(box).encode("utf-8")] = self._getTemplate(box, self._content)

        return dict

    def __is_XXTemplate(self, infobox, key_list, template_list):
        for key in infobox.keys():
            key = str(key)
            if key in key_list:
                for i in template_list:
                    if self._getTemplate(i, infobox[key].lower()):
                        return {"result": True, "key": key}
                return {"result": False, "key": key}
        return {"result": None, "key":""}

    def is_birthDateTemplate(self, infobox):
        key_list = [
        "doğum_tarihi",
        "dogum_tarihi",
        "doğum tarihi"
        "dogum tarihi",
        "doğumtarihi",
        "dogumtarihi"
        ]

        template_list = [
        "doğum tarihi",
        "doğum tarihi ve yaşı"
        ]

        return self.__is_XXTemplate(infobox, key_list, template_list)

    def is_deathDateTemplate(self, infobox):
        key_list = [
        "ölüm_tarihi",
        "olum_tarihi",
        "ölüm tarihi"
        "olum tarihi",
        "ölümtarihi",
        "olumtarihi"
        ]

        template_list = [
        "ölüm tarihi",
        "ölüm tarihi ve yaşı"
        ]

        return self.__is_XXTemplate(infobox, key_list, template_list)

    @staticmethod
    def __turkishDateFormatToDefault(text):
        months_turkish=[
        "Ocak",
        "Şubat",
        "Mart",
        "Nisan",
        "Mayıs"
        ]

    def _fixBirthDate(self, infobox, isList=False):
        text = infobox[self.is_birthDateTemplate(infobox)["key"]]
        if self.is_birthDateTemplate(infobox)["result"] is False:
            resolve = BeautifulSoup(text, 'html.parser')
            if resolve:
                text = infobox[self.is_birthDateTemplate(infobox)["key"]]
                try:
                    text_list = text.split(str(resolve.find_all()[0]))
                    text_list[1] = str(resolve.find_all()[0]) + text_list[1]
                except:
                    text_list = [text]
                if timestring.Date(text_list[0]):
                    try:
                        text_list[0] = str(text_list[0]).encode("utf-8").replace("[[", "")
                        text_list[0] = str(text_list[0]).encode("utf-8").replace("]]", "")
                        birthDate = datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%d %B %Y")
                    except:
                        raise ValueError("The format must be 'dd mm yy'.")
                    if ( self.is_deathDateTemplate(infobox)["result"] is False and not self.is_deathDateTemplate(infobox)["key"] ):
                        fixBirth = "{{" + "Doğum tarihi ve yaşı|{year}|{month}|{day}".format(year=birthDate.year, month=birthDate.month, day=birthDate.day) + "}}"
                    else:
                        fixBirth = "{{" + "Doğum tarihi|{year}|{month}|{day}".format(year=birthDate.year, month=birthDate.month, day=birthDate.day) + "}}"

                    text_list[0] = fixBirth
        try:
            if not isList:
                return "".join(text_list)
            else:
                return text_list
        except:
            return text

    def _fixDeathDate(self, infobox):
        try:
            text = infobox[self.is_deathDateTemplate(infobox)["key"]]
        except:
            text = ""
        if self.is_deathDateTemplate(infobox)["result"] is False:
            resolve = BeautifulSoup(text, 'html.parser')
            if resolve:
                text = infobox[self.is_deathDateTemplate(infobox)["key"]]
                try:
                    text_list = text.split(str(resolve.find_all()[0]))
                    text_list[1] = str(resolve.find_all()[0]) + text_list[1]
                except:
                    text_list = [text]

                if timestring.Date(text_list[0]):
                    try:
                        text_list[0] = text_list[0].replace("[[", "")
                        text_list[0] = text_list[0].replace("]]", "")
                        try:
                            m = re.search("((\w+) yaşında)", text_list[0])
                            print m.groups()
                            text_list[0] = text_list[0][:(text_list[0].find("(" + m.groups()[0] + ")")-1)]
                        except:
                            pass
                        deathDate = datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%d %B %Y")
                    except:
                        raise ValueError("The format must be 'dd mm yy'.")
                    #if not ( self.is_birthDateTemplate(infobox)["result"] is False and not self.is_birthDateTemplate(infobox)["key"] ):
                    if self.is_birthDateTemplate(infobox)["result"] is True:
                        birthDate = self._getTemplate("Doğum tarihi", self._fixBirthDate(infobox))
                        fixBirth = "{{" + "Ölüm tarihi ve yaşı|{death_year}|{death_month}|{death_day}|{birth_year}|{birth_month}|{birth_day}".format(
                        death_year=deathDate.year,
                        death_month=deathDate.month,
                        death_day=deathDate.day,
                        birth_year=birthDate[0],
                        birth_month=birthDate[1],
                        birth_day=birthDate[2]) + "}}"
                    else:
                        fixBirth = "{{" + "Ölüm tarihi|{death_year}|{death_month}|{death_day}".format(
                        death_year=deathDate.year,
                        death_month=deathDate.month,
                        death_day=deathDate.day) + "}}"

                    if fixBirth:
                        text_list[0] = fixBirth
        try:
            return "".join(text_list)
        except:
            return text

    def fixBirthAndDeathDates(self):
        for key, val in self.infoboxes.iteritems():
            if self.is_birthDateTemplate(val)["result"] is False:
                try:
                    self.infoboxes[key][self.is_birthDateTemplate(val)["key"]] = self._fixBirthDate(val)
                except:
                    pass
            if self.is_deathDateTemplate(val)["result"] is False:
                try:
                    self.infoboxes[key][self.is_deathDateTemplate(val)["key"]] = self._fixDeathDate(val)
                except:
                    pass

    @staticmethod
    def _templateToString(name, dict):
        result="{{"+name+"\n"
        for key, val in dict.iteritems():
            if str(key) != "0":
                result += "| "+str(key)+" = "+str(val)+"\n"
        result += "}}"
        return result


    def render(self):
        new_content = self._content
        for key, value in self.infoboxes.iteritems():
            indexes = self._getStartEndIndexOfTemplate(key, new_content)
            new_content = new_content.replace(new_content[indexes[0]:indexes[1]], self._templateToString(key, value))
        return new_content
