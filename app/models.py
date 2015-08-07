#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wikitools import wiki, category, api, page
from bs4 import BeautifulSoup
import locale, datetime, sys, timestring, re
from collections import OrderedDict

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
                break
        return [startIndex-2-len(infobox_name), endIndex+2]

    def _getTemplate(self, name, content):
        input = content

        resolve = BeautifulSoup(input, 'html.parser')
        for n in resolve.find_all():
            old = n
            try:
                n.replace("|", "%!%!%")
            except:
                pass
            try:
                n.replace("=", "%@%@%")
            except:
                pass
        try:
            if n:
                input.replace(old, n)
        except:
            pass

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

                #asd
                parts = result.split("|")
                dict = OrderedDict()
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
                        if self._getTemplate(i, content):
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
        "doğum tarihi ve yaşı",
        "doğum yılı",
        "doğum yılı ve yaşı"
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
        "ölüm tarihi ve yaşı",
        "ölüm yılı",
        "ölüm yılı ve yaşı"
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
        excepts = ["hayatta", "yaşıyor", "-", ""]
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

                text_list[0] = str(text_list[0]).encode("utf-8").replace("[[", "")
                text_list[0] = str(text_list[0]).encode("utf-8").replace("]]", "")

                try:
                    timestring.Date(text_list[0])
                    control1 = True
                except:
                    try:
                        datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%B %Y")
                        control1 = True
                    except:
                        try:
                            datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%Y")
                            control1 = True
                        except:
                            control1 = False

                try:
                    datetime.datetime.strptime(text_list[0], '%d %B %Y')
                    control2 = True
                except:
                    control2 = False

                #None= only year, False= month and year, True= all
                date_control = None
                if control1 or control2:
                    try:
                        try:
                            birthDate = datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%B %Y")
                            date_control = False
                        except:
                            try:
                                birthDate = datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%Y")
                                date_control = None
                            except:
                                birthDate = datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%d %B %Y")
                                date_control = True
                    except:
                        raise ValueError("The format must be 'dd mm yy'.")

                    if ( self.is_deathDateTemplate(infobox)["result"] is False and ((not infobox[self.is_deathDateTemplate(infobox)["key"]])) or infobox[self.is_deathDateTemplate(infobox)["key"]] in excepts ) or self.is_deathDateTemplate(infobox)["result"] is None:
                        if date_control is None:
                            fixBirth = "{{" + "Doğum yılı ve yaşı|{year}".format(year=str(birthDate.year)) + "}}"
                        elif date_control is False:
                            fixBirth = "{{" + "Doğum yılı ve yaşı|{year}|{month}".format(year=str(birthDate.year), month=str(birthDate.month)) + "}}"
                        else:
                            fixBirth = "{{" + "Doğum tarihi ve yaşı|{year}|{month}|{day}".format(year=str(birthDate.year), month=str(birthDate.month), day=str(birthDate.day)) + "}}"
                    else:
                        if date_control is True:
                            fixBirth = "{{" + "Doğum tarihi|{year}|{month}|{day}".format(year=str(birthDate.year), month=str(birthDate.month), day=str(birthDate.day)) + "}}"
                        else:
                            fixBirth = str(birthDate.year)

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

                text_list[0] = text_list[0].replace("[[", "")
                text_list[0] = text_list[0].replace("]]", "")

                try:
                    timestring.Date(text_list[0])
                    control1 = True
                except:
                    try:
                        datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%B %Y")
                        control1 = True
                    except:
                        try:
                            datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%Y")
                            control1 = True
                        except:
                            control1 = False

                try:
                    datetime.datetime.strptime(text_list[0], '%d %B %Y')
                    control2 = True
                except:
                    control2 = False

                #None= only year, False= month and year, True= all
                date_control = None

                if control1 or control2:

                    try:
                        try:
                            m = re.search("((\w+) yaşında)", text_list[0])
                            text_list[0] = text_list[0][:(text_list[0].find("(" + m.groups()[0] + ")")-1)]
                        except:
                            try:
                                m = re.search("((\w+) yaşlarında)", text_list[0])
                                text_list[0] = text_list[0][:(text_list[0].find("(" + m.groups()[0] + ")")-1)]
                            except:
                                pass

                        try:
                            deathDate = datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%B %Y")
                            date_control = False
                        except:
                            try:
                                deathDate = datetime.datetime.strptime(text_list[0], "%Y")
                                date_control = None
                            except:
                                deathDate = datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%d %B %Y")
                                date_control = True


                    except:
                        raise ValueError("The format must be 'dd mm yy'.")
                    #if not ( self.is_birthDateTemplate(infobox)["result"] is False and not self.is_birthDateTemplate(infobox)["key"] ):

                    if self.is_birthDateTemplate(infobox)["result"] is True:
                        if date_control is None or date_control is False:
                            try:
                                birthDate = self._getTemplate("Doğum tarihi", self._fixBirthDate(infobox))
                                year=str(birthDate[0])
                            except:
                                year = str(infobox[self.is_birthDateTemplate(infobox)["key"]])

                            if date_control is None:
                                fixBirth = "{{" + "Ölüm yılı ve yaşı|{death_year}|{birth_year}".format(
                                death_year=str(deathDate.year),
                                birth_year=year) + "}}"
                            else:
                                fixBirth = "{{" + "Ölüm yılı ve yaşı|{death_year}|{birth_year}|{death_month}".format(
                                death_year=str(deathDate.year),
                                birth_year=year,
                                death_month=str(deathDate.month)) + "}}"
                        else:
                            birthDate = self._getTemplate("Doğum tarihi", self._fixBirthDate(infobox))
                            fixBirth = "{{" + "Ölüm tarihi ve yaşı|{death_year}|{death_month}|{death_day}|{birth_year}|{birth_month}|{birth_day}".format(
                            death_year=str(deathDate.year),
                            death_month=str(deathDate.month),
                            death_day=str(deathDate.day),
                            birth_year=birthDate[0],
                            birth_month=birthDate[1],
                            birth_day=birthDate[2]) + "}}"
                    else:
                        if date_control is None or date_control is False:
                            try:
                                birthDate = self._getTemplate("Doğum tarihi", self._fixBirthDate(infobox))
                                year=str(birthDate[0])
                            except:
                                year = str(infobox[self.is_birthDateTemplate(infobox)["key"]])

                            if date_control is None:
                                fixBirth = "{{" + "Ölüm yılı ve yaşı|{death_year}|{birth_year}".format(
                                death_year=str(deathDate.year),
                                birth_year=year) + "}}"
                            else:
                                fixBirth = "{{" + "Ölüm yılı ve yaşı|{death_year}|{birth_year}|{death_month}".format(
                                death_year=str(deathDate.year),
                                birth_year=year,
                                death_month=str(deathDate.month)) + "}}"
                        else:
                            fixBirth = "{{" + "Ölüm tarihi|{death_year}|{death_month}|{death_day}".format(
                            death_year=str(deathDate.year),
                            death_month=str(deathDate.month),
                            death_day=str(deathDate.day)) + "}}"


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
        max_key_len = 1

        for key, val in dict.iteritems():
            if str(key) != "0":
                if max_key_len < int(len(key.strip().decode('utf-8'))):
                    max_key_len = int(len(key.strip().decode('utf-8')))

        for key, val in dict.iteritems():
            if str(key) != "0":
                spaces = " "*(max_key_len - len(str(key).strip().decode('utf-8')))
                result += "| "+str(key)+spaces+" = "+str(val)+"\n"

        result += "}}"
        return result


    def render(self):
        new_content = self._content
        for key, value in self.infoboxes.iteritems():
            indexes = self._getStartEndIndexOfTemplate(key, new_content)

            #birth = self.is_birthDateTemplate(value)
            #death = self.is_deathDateTemplate(value)

            #if birth["result"] is True:
            #    if re.findall("{}[ \n]+)=".format(birth["key"]) ,new_content):
            #        fi = new_content.find("{}{}=".format(birth["key"], re.findall(birth["key"]+"[ \n]+)=" ,new_content)[0]))
            #        for i in [n for n in xrange(len(new_content)) if fi == n]:
            #            if i <= new_content.find(value[birth]) <= indexes[1]:
            #                ram = new_content[i:indexes[1]]
            #                ram.replace(self.findInfoboxes()[key][birth["key"]], value[birth["key"]], 1)
            #                print "kk"
            #                new_content.replace(new_content[i:indexes[1]], ram, 1)
            #if death["result"] is True:
            #    print str(death["key"])
            #    tt = str(death["key"])+"[ \n]+)="
            #    print re.findall(tt , new_content[indexes[0]:indexes[1]])
            #    if re.findall(tt , new_content):
            #        fi = new_content.find("{}{}=".format(death["key"], re.findall(death["key"]+"[ \n]+)=" ,new_content)[0]))
            #        for i in [n for n in xrange(len(new_content)) if fi == n]:
            #            if i <= new_content.find(value[birth]) <= indexes[1]:
            #                ram = new_content[i:indexes[1]]
            #                ram.replace(self.findInfoboxes()[key][death["key"]], value[death["key"]], 1)
            #                print "kk"
            #                new_content.replace(new_content[i:indexes[1]], ram, 1)

            #        #if indexes[0] <= new_content.find("{}{}=".format(birth["key"], re.findall(birth["key"]+"[ \n]+)=" ,a)[0])) <= indexes[1]:


            new_content = new_content.replace(new_content[indexes[0]:indexes[1]], self._templateToString(key, value))
        return new_content
