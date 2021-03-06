#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import urllib.request
from html.parser import HTMLParser
import math
import json



class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inTable = False
        self.inTr = False
        self.inTh = False
        self.inTd = False

        self.lastTag = "html"
        self.lastTh = ""
        self.lastTd = ""

        self.keys = {}

    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        if tag == "table":
            self.inTable = True
        elif tag == "tr":
            self.inTr = True
        elif tag == "th":
            self.inTh = True
        elif tag == "td":
            self.inTd = True

    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        if tag == "table":
            self.inTable = False
        elif tag == "tr":
            self.inTr = False
        elif tag == "th":
            self.inTh = False
        elif tag == "td":
            self.inTd = False
        self.lastTag = tag
    def handle_data(self, data):
        #print("Encountered some data  :", data)
        if self.inTable:
            if self.inTr:
                if self.inTh:
                   # print('Type:', data)
                    self.lastTh = data
                elif self.inTd:
                    #print('Data:', data)
                    #print(self.lastTag)
                    if self.lastTag == "th":
                        if data != "Click for Further Information":
                            #print("Dataset key=" + self.lastTh + "data=" + data)
                            self.keys[self.lastTh] = data
                        else:
                            pass
                            #print("Skipping dummy info")





class PageGetter:

    def __init__(self, url, encoding, parser):
        self.SITE_URL = url
        self.ENCODING = encoding
        self.retrieveData()
        self.parser = parser
    def retrieveData(self):
        response = urllib.request.urlopen(self.SITE_URL)
        self.rawHtml = response.read()
        self.decodedHtml = self.rawHtml.decode(self.ENCODING, "ignore")
    def tableCheck(self):
        if "<table" in self.decodedHtml:
            return True
        else:
            return False
    def feedParser(self):
        self.parser.feed(self.decodedHtml)
        #print(self.parser.keys)
        outputString = json.dumps(self.parser.keys)
        return self.parser.keys
    def testOutput(self):
        print('===Decoded html output:===')
        print(self.decodedHtml)

class PageIncrement:

    def __init__(self, baseurl):
        self.BASE_URL = baseurl
        self.currentPage = 1
    def generateUrl(self):
        self.currentPageUrl = self.BASE_URL + str(self.currentPage)
        return self.currentPageUrl
    def incrementUrl(self):
        self.currentPage += 1

class PageGroup:

    def __init__(self, groupKey, groupValue, dataset):
        self.GROUP_KEY = groupKey
        self.GROUP_VALUE = groupValue
        self.DATASET = dataset
        self.pages = []
        self.createGroup()
    def createGroup(self):
        for person in self.DATASET:
            if self.GROUP_KEY in person:
                if person[self.GROUP_KEY] == self.GROUP_VALUE:
                    self.pages.append(person)
    def getGroupData(self):
        return self.pages


def progressBar(pos, highest, scrWidth):
    charPos = int(math.floor((pos / highest) * scrWidth))
    for i in range(0, charPos):
        print('+', end='')
    print()

def main():
    SITE_URL = "http://www.sheffieldsoldierww1.co.uk/"
    BASE_URL = "http://www.sheffieldsoldierww1.co.uk/search4.php?id="


    urlGen = PageIncrement(BASE_URL)
    jsonKeys = []

    finishedReading = False
    count = 0
    COUNT_MAX = 20

    while not finishedReading and count < COUNT_MAX:
        parser = MyHTMLParser()
        currentUrl = urlGen.generateUrl()
        #print(currentUrl)
        currentPage = PageGetter(currentUrl, "utf-8", parser)
        if not currentPage.tableCheck():
            finishedReading = True
        else:
            jsonKeys.append(currentPage.feedParser())
            #print(currentPage.testOutput())

            print("Reading page " + str(count + 1) + "/" + str(COUNT_MAX) + "...")
            progressBar(count, COUNT_MAX, 80)

            count += 1
            urlGen.incrementUrl()

    print("Total read: " + str(count) + " pages.")
    #print(jsonKeys)
    fileOutput = json.dumps(jsonKeys)
    with open("test.json", "w") as fp:
        fp.write(fileOutput)

    surnameAbbey = PageGroup("Surname", "Abbey", jsonKeys)
    print(surnameAbbey.getGroupData())


if __name__ == '__main__': main()
