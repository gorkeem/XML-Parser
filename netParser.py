import xml.etree.cElementTree as ET
import os
import shutil
import sys
import json
from bottle import route, run, template, static_file, request, redirect

info = {"planName"         :"XML Parser",
        "netVersion"       :"0.0.1",
        "planDate"         :"05.07.2019",
        "parsedData"       :{},
        "sections"         :[]
        }
        
def xmlBrowse(name):
    xmlName = ET.parse("./"+name)
    collectInfo(xmlName)

def collectInfo(netXml):
    getSections(netXml)
    getInfo(netXml)

def getSections(netXml):
    root = netXml.getroot()
    for item in root:
        info["sections"].append(tagToText(item.tag))
    info["sections"].sort()

def getInfo(netXml):
    root = netXml.getroot()
    for item in root:
        info["parsedData"][item.tag] = []
        radioRelation = ""
        planradId = ""
        myAppend = ""
        subItemText = "."

        for subitem in item.iter():
            if subitem.text != None:
                subItemText = subitem.text

            tagVal = str(subitem.tag)
            attribVal = str("%s" % subitem.attrib)

            semicolIndex = attribVal.find(":")
            singleQuoteIndex = attribVal.find("'", semicolIndex + 3) if semicolIndex != -1 else -1
            attribVal = attribVal[semicolIndex + 3: singleQuoteIndex] if "{}" not in attribVal else "NotAvailable"

            txt = tagVal + " " + attribVal + 'TEXT: ' + subItemText
            info["parsedData"][item.tag].append(txt)

def tagToText(tag):
    return ' '.join([word.capitalize() for word in tag.split('_')])

@route('/<pathName>/<filename>')
def getDependency(pathName, filename):
    return_file = '{0}/{1}'.format(pathName, filename)

    # 1. Check if that file exists.
    exists = os.path.isfile('http/' + return_file)
    # 2. If exist, return with that file.
    if exists and ('.html' in filename):
        if "content" == pathName:
            return_file = 'http/' + return_file
            return template(return_file, info=info)
    # 3. If file does not exists, create that file.
    else:
        if '.html' in filename:
            # Copy the none.html
            dst_dir = os.path.join('http/content')
            src_file = os.path.join('http/content/none/none.html')
            shutil.copy(src_file, dst_dir)

            # Rename the copied file
            dst_file = os.path.join(dst_dir, 'none.html')
            new_dst_file_name = os.path.join(dst_dir, filename)
            os.rename(dst_file, new_dst_file_name)

            # Fill with info
            fil = filename.replace('.html', '')
            with open("http/content/" + filename, "r+", encoding="utf-8") as f:
                old = f.read()
                f.seek(0)
                f.write(old.replace('GORKEM', fil))
                f.close()

            if ("content" == pathName):
                return_file = 'http/' + return_file
                return template(return_file, info=info)

    return static_file(return_file, root='./http')

@route('/content/<sectionName>')
def showContentInfo():
    return template('http/content/<sectionName>', info=info)

@route('/')
def getReport():
    return template('http/index', info=info)

@route('/upload', method='POST')
def upload():
    fileUpload = request.files.fileUpload
    fileUpload.save("./" + fileUpload.filename, overwrite=True)
    if fileUpload.filename[-4:] != ".xml":
        print("CHOOSE AN XML FILE")
        return redirect("/")
    global info
    info = {"planName"          :"XML Parser",
            "netVersion"        :"0.0.1",
            "planDate"          :"05.07.2019",
            "parsedData"        : {},
            "sections"          : []
            }
    xmlBrowse(fileUpload.filename)
    print(info["sections"])
    return redirect("/")

def Main():
    
    run(host='localhost', port=5000)

if __name__ == "__main__":
    Main()