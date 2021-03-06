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
        if content.find("Futbolcu bilgi kutusu2") != -1:
            self._content = content.encode("utf-8").replace("Futbolcu bilgi kutusu2", "Futbolcu bilgi kutusu")
        else:
            self._content = content.encode("utf-8")
        self.infoboxes = self.findInfoboxes()
        self.infoboxNames = self._findInfoboxesName()

    #It finds start-end indexes of the template.
    @staticmethod
    def _getStartEndIndexOfTemplate(infobox_name, content):
        input = content
        length = len(input)
        endIndex = 0
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

    #It finds the template and exports as dict it.
    def _getTemplate(self, name, content):
        input = content
        #It changes some codes for process without bugs.
        input = input.replace("<br>", "<br/>").replace("</br>", "<br/>").replace("|df=yes", "").replace("|df=y", "").replace("|mf=yes", "").replace("|mf=y", "")
        input = BeautifulSoup(input, 'html.parser', from_encoding="utf-8").decode()

        resolve = BeautifulSoup(input, 'html.parser', from_encoding="utf-8")

        #It finds HTML codes and changes them for process without bugs.
        for i in resolve.findChildren():
            old = str(i)
            i = str(i).replace("|", "%!%!%").replace("=", "%@%@%")
            if old != i:
                input = input.replace(old, i)

        input = input.encode('utf-8').replace('/">', '" />').replace("/'>", "' />")

        for i in re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', input):
            new = i
            new = new.replace("|", "%!%!%").replace("=", "%@%@%")
            input = input.replace(i, new)

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
                #i[7:] for 'Şablon:'. i[9:] for 'Template:'.
                i = i[7:]
                try:
                    if content.find(i) != -1 and str(i).endswith("bilgi kutusu"):
                        if self._getTemplate(i, content):
                            list.append(i)
                except:
                    pass

        newlist = []

        for i in list:
            if not i in newlist:
                newlist.append(i)

        di = {}

        for i in newlist:
            di[i] = self._getStartEndIndexOfTemplate(i, content)

        keylist = di.keys()
        keylist.sort()

        return [i.encode("utf-8") for i in keylist]

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
                try:
                    key
                except:
                    key = ""
                return {"result": False, "key": key}
        return {"result": None, "key":""}

    def is_birthDateTemplate(self, infobox):
        key_list = [
        "doğum_tarihi",
        "dogum_tarihi",
        "doğum tarihi",
        "dogum tarihi",
        "doğumtarihi",
        "dogumtarihi",
        "Doğum",
        "doğum",
        "birth_date",
        "birthdate"
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
        "ölüm tarihi",
        "olum tarihi",
        "ölümtarihi",
        "olumtarihi",
        "Ölüm",
        "ölüm",
        "death_date",
        "deathbirth"
        ]

        template_list = [
        "ölüm tarihi",
        "ölüm tarihi ve yaşı",
        "ölüm yılı",
        "ölüm yılı ve yaşı"
        ]

        return self.__is_XXTemplate(infobox, key_list, template_list)

    @staticmethod
    def _is_in_infobox(infobox, key):
        if key in infobox.keys():
            return infobox[key]
        else:
            return False

    def _fixBirthDate(self, infobox, isList=False):
        excepts = ["hayatta", "yaşıyor", "-", "", "<!-- {{ölüm tarihi ve yaşı|yıl|ay|gün}} -->", "<!-- {{Ölüm tarihi ve yaşı|yıl|ay|gün}} -->", "<!-- {{ölüm tarihi|yıl|ay|gün}} -->", "<!-- {{Ölüm tarihi|yıl|ay|gün}} -->"]
        text = infobox[self.is_birthDateTemplate(infobox)["key"]]
        if self.is_birthDateTemplate(infobox)["result"] is False:
            resolve = BeautifulSoup(text, 'html.parser', from_encoding="utf-8")
            if resolve:
                try:
                    if resolve.findChildren():
                        separators = [x.encode('utf-8') for x in resolve.findChildren()]
                        separators_text = ""
                        for i in separators:
                            if i is not None:
                                if separators.index(i) == 0:
                                    separators_text =+ "("+i+")"
                                else:
                                    separators_text =+ "|("+i+")"
                                    text_list = re.split(separators_text, text)
                    else:
                        text_list = [text]
                except:
                    text_list = [text]

                sss = []
                sss.append(text_list[0].split(",")[0])
                sss.extend([ "," + x for x in text_list[0].split(",")[1:]])
                sss.extend(text_list[1:])

                text_list = sss

                backup_text_list = text_list[0]

                text_list[0] = text_list[0].strip()

                text_list[0] = str(text_list[0]).encode("utf-8").replace("[[", "")
                text_list[0] = str(text_list[0]).encode("utf-8").replace("]]", "")

                #It controls whether it matches the date format or not.
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
                                birthDate = datetime.datetime.strptime(text_list[0], "%Y")
                                date_control = None
                            except:
                                birthDate = datetime.datetime.strptime(str(text_list[0]).encode("utf-8"), "%d %B %Y")
                                date_control = True

                    except:
                        raise ValueError("The format must be 'dd mm yy'.")

                    if ( self.is_deathDateTemplate(infobox)["result"] is False and (not self._is_in_infobox(infobox, self.is_deathDateTemplate(infobox)["key"])) or self._is_in_infobox(infobox, self.is_deathDateTemplate(infobox)["key"]) in excepts ) or self.is_deathDateTemplate(infobox)["result"] is None:
                        if date_control is None:
                            fixBirth = "{{" + "Doğum yılı ve yaşı|{year}".format(year=str(birthDate.year)) + "}}"
                        elif date_control is False:
                            fixBirth = "{{" + "Doğum yılı ve yaşı|{year}|{month}".format(year=str(birthDate.year), month=str(birthDate.month)) + "}}"
                        else:
                            fixBirth = "{{" + "Doğum tarihi ve yaşı|{year}|{month}|{day}".format(year=str(birthDate.year), month=str(birthDate.month), day=str(birthDate.day)) + "}}"
                    else:
                        if date_control is True:
                            fixBirth = "{{" + "Doğum tarihi|{year}|{month}|{day}".format(year=str(birthDate.year), month=str(birthDate.month), day=str(birthDate.day)) + "}}"
                        elif date_control is False:
                            fixBirth = backup_text_list
                        elif date_control is None:
                            fixBirth = str(birthDate.year)

                    text_list[0] = fixBirth
                elif not control1 and not control2:
                    text_list[0] = backup_text_list
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

        text = text.replace("<br>", "<br/>")

        if self.is_deathDateTemplate(infobox)["result"] is False:
            resolve = BeautifulSoup(text, 'html.parser', from_encoding="utf-8")
            if resolve:
                try:
                    if resolve.findChildren():
                        separators = [x.encode('utf-8') for x in resolve.findChildren()]
                        separators_text = ""
                        for i in separators:
                            if i is not None:
                                if separators.index(i) == 0:
                                    separators_text =+ "("+i+")"
                                else:
                                    separators_text =+ "|("+i+")"
                                    text_list = re.split(separators_text, text)
                    else:
                        text_list = [text]
                except:
                    text_list = [text]

                sss = []
                sss.append(text_list[0].split(",")[0])
                sss.extend([ "," + x for x in text_list[0].split(",")[1:]])
                sss.extend(text_list[1:])

                text_list = sss

                backup_text_list = text_list[0]

                text_list[0] = text_list[0].strip()

                text_list[0] = text_list[0].replace("[[", "")
                text_list[0] = text_list[0].replace("]]", "")

                for text in text_list:
                    old = text
                    try:
                        m = re.search("((\w+) yaşında)", text)
                        text = text.replace("(" + m.groups()[0] + ")", "")
                        #text = text[:(text.find("(" + m.groups()[0] + ")")-1)]
                    except:
                        try:
                            m = re.search("((\w+) yaşlarında)", text)
                            text = text.replace("(" + m.groups()[0] + ")", "")
                        except:
                            try:
                                m = re.search("((\w+) yaş)", text)
                                text = text.replace("(" + m.groups()[0] + ")", "")
                            except:
                                try:
                                    m = re.search("((\w+) Yaşında)", text)
                                    text = text.replace("(" + m.groups()[0] + ")", "")
                                except:
                                    pass

                    if text == ", " and len(text_list) >= text_list.index(old)+1:
                        del text_list[text_list.index(old)]
                    else:
                        text_list[text_list.index(old)] = text

                if len(text_list) == 1 and text_list[0][-1] == " ":
                    text_list[0] = text_list[0][:-1]

                #It controls whether it matches the date format or not.
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

                    if self.is_birthDateTemplate(infobox)["result"] is True and infobox[self.is_birthDateTemplate(infobox)["key"]].lower().find("doğum tarihi ve yaşı") == -1:
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

                    elif infobox[self.is_birthDateTemplate(infobox)["key"]].lower().find("doğum tarihi ve yaşı") == -1:
                        if date_control is None or date_control is False:
                            try:
                                birthDate = self._getTemplate("Doğum tarihi", self._fixBirthDate(infobox))
                                year=str(birthDate[0])
                            except:
                                year = str(infobox[self.is_birthDateTemplate(infobox)["key"]])
                                try:
                                    datetime.datetime.strptime(year, "%Y")

                                    if date_control is None:
                                        fixBirth = "{{" + "Ölüm yılı ve yaşı|{death_year}|{birth_year}".format(
                                        death_year=str(deathDate.year),
                                        birth_year=year) + "}}"
                                    else:
                                        fixBirth = "{{" + "Ölüm yılı ve yaşı|{death_year}|{birth_year}|{death_month}".format(
                                        death_year=str(deathDate.year),
                                        birth_year=year,
                                        death_month=str(deathDate.month)) + "}}"
                                except:
                                    fixBirth = text_list[0]

                        else:
                            fixBirth = "{{" + "Ölüm tarihi|{death_year}|{death_month}|{death_day}".format(
                            death_year=str(deathDate.year),
                            death_month=str(deathDate.month),
                            death_day=str(deathDate.day)) + "}}"
                    if fixBirth:
                        text_list[0] = fixBirth

                elif not control1 and not control2:
                    text_list[0] = backup_text_list

        if self.is_deathDateTemplate(infobox)["result"] is True and text.lower().find("ölüm tarihi ve yaşı") == -1:
            try:
                text_list
            except:
                def if_first_is_str(the_dict):
                    try:
                        int(the_dict[0])
                    except:
                        del the_dict[0]
                    return the_dict

                if len(self._getTemplate("Ölüm tarihi", text).keys()) <= 4 and (self.is_birthDateTemplate(infobox)["result"] is True and infobox[self.is_birthDateTemplate(infobox)["key"]].lower().find("doğum tarihi ve yaşı") == -1):
                    birthDate = if_first_is_str(self._getTemplate("Doğum tarihi", self._fixBirthDate(infobox)))
                    deathDate = if_first_is_str(self._getTemplate("Ölüm tarihi", text.encode("utf-8")))

                    indexes = self._getStartEndIndexOfTemplate("ölüm tarihi", text.lower().encode("utf-8"))

                    text = text.replace(text[indexes[0]:indexes[1]], "{{"+"Ölüm tarihi ve yaşı|{death_year}|{death_month}|{death_day}|{birth_year}|{birth_month}|{birth_day}".format(
                    death_year = deathDate.values()[0],
                    death_month = deathDate.values()[1],
                    death_day = deathDate.values()[2],
                    birth_year = birthDate.values()[0],
                    birth_month = birthDate.values()[1],
                    birth_day = birthDate.values()[2]
                    )+"}}")
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

            if self.is_deathDateTemplate(val)["result"] is False or self.is_deathDateTemplate(val)["result"] is True:
                try:
                    self.infoboxes[key][self.is_deathDateTemplate(val)["key"]] = self._fixDeathDate(val)
                except:
                    pass

    #It converts the template to string.
    @staticmethod
    def _templateToString(name, dict):
        result="{{"+name+"\n"
        max_key_len = 1

        for key, val in dict.iteritems():
            if str(key) != "0":
                if max_key_len < int(len(str(key).strip().decode('utf-8'))):
                    max_key_len = int(len(str(key).strip().decode('utf-8')))

        for key, val in dict.iteritems():
            if str(key) != "0":
                spaces = " "*(max_key_len - len(str(key).strip().decode('utf-8')))
                result += "| "+str(key)+spaces+" = "+str(val)+"\n"

        result += "}}"
        return result

    #It renders the content with new template.
    def render(self):
        new_content = self._content

        for key, value in self.infoboxes.iteritems():
            indexes = self._getStartEndIndexOfTemplate(key, new_content)
            new_content = new_content.replace(new_content[indexes[0]:indexes[1]], self._templateToString(key, value))
        return new_content
