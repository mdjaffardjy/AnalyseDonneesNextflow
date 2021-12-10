from wfNextflow import *
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns
import json

class bold_color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def createDicoWfN(data):
    currentPath = os.getcwd()
    dicoWf= {}
    nbWf = len(data.keys())
    idx = 1
    for bigNames in data:
        print("WORKFLOW : ", idx , "/", nbWf)
        idx +=1
        url = "https://github.com/" + bigNames
        files = data[bigNames]["files"]
        name = data[bigNames]["name"] 
        creation_date = data[bigNames]["creation_date"]
        actual_date = data[bigNames]["actual_date"]
        last_push = data[bigNames]["last_push"]
        owner = data[bigNames]["owner"]
        description = data[bigNames]["description"]
        forks = data[bigNames]["forks"]
        stars = data[bigNames]["stars"]
        link = data[bigNames]["link"]

        nameFolder = bigNames.replace("/", "_")
        os.chdir(currentPath)
        #print(currentPath)
        #os.chdir("../Workflows/bddFiles")
        try :
            os.chdir("../Workflows/bddFiles/" + nameFolder)
        except:
            os.chdir("../Workflows/bddFiles")
            os.system("mkdir " + nameFolder)
            os.chdir(currentPath)
            os.chdir("../Workflows/bddFiles/" + nameFolder)

        wfN = Nextflow_WF(url, files, name, nameFolder, creation_date, actual_date, last_push, owner, description, forks, stars)
        wfN.extract()
        dicoWf.update({bigNames : wfN})
    os.chdir(currentPath)   
    return dicoWf

def extractToolsAnnotations(dicoWf):
    nbTools = {}
    for wfn in dicoWf:
        wf = dicoWf[wfn]
        dejaVu = []
        tools = wf.getAnnotations()
        for t in tools:
            tt = tools[t]['name']
            if not tt in dejaVu:
                if not  tt in nbTools:
                    nbTools.update({tt:1})
                else:
                    nbTools[tt] += 1
                dejaVu.append(tt)
    nbToolsPerWf = {}
    fileTools = open("nextflowTools.txt", "w")
    for k, v in sorted(nbTools.items(), key=lambda x: x[1], reverse=True):
        nbToolsPerWf.update({k:v})
        fileTools.write(k + " : " + str(v) + "\n")
    return nbToolsPerWf

def analysePartProcess(dicoWf):
    fileInfo = open("InfoWfNextflow/statPartsAll.csv", "w")
    txt = "Database worflow size : {}\n".format(len(dicoWf))
    fileInfo.write(txt)
    txt = "\tPresent\tNot Present\n"
    fileInfo.write(txt)
    keywordAll = {'directives':0, 'input':0, 'output':0, 'when':0, 'script':0, 'stub':0}
    languageScriptAll = {}
    nbTot = 0
    nbTotProcess = 0
    for wfn in dicoWf:
        wf = dicoWf[wfn]
        string = "InfoWfNextflow/statParts_" + wf.getNameFolder()+ ".csv"
        keyword = {'directives':0, 'input':0, 'output':0, 'when':0, 'script':0, 'stub':0}
        languageScript = {}
        fileInfoWf = open(string, "w")
        dicoProcess = wf.getProcess()
        txt = "Database process size : {}\n".format(len(dicoProcess))
        fileInfoWf.write(txt)
        txt = "\tPresent\tNot Present\n"
        fileInfoWf.write(txt)
        for name in dicoProcess:
            nbTotProcess += 1
            nbTot += 1
            informations = dicoProcess[name].getAll()
            for part, k in zip(informations[1:], keyword):
                if part != None:
                    keyword[k] += 1
                    keywordAll[k] +=1
                if k == 'script'and part != None:
                    l = part.getLanguage()
                    if l in languageScript:
                        languageScript[l] +=1
                    else:
                        languageScript.update({l: 1})
                        
                    if l in languageScriptAll:
                        languageScriptAll[l] +=1
                    else :
                        languageScriptAll.update({l: 1})


        for k in keyword:
            nb = keyword[k]
            nb2 = len(dicoProcess) - keyword[k]
            txt = "{}\t{}\t{}\n".format(k, nb, nb2)
            fileInfoWf.write(txt)
        fileInfoWf.write("\n")
        for l in languageScript:
            txt = "{}\t{}\n".format(l, languageScript[l])
            fileInfoWf.write(txt)
        for _ in range (3):
            fileInfoWf.write("\n")
    
    fileInfo.write("Numbers of process : {}\n".format(nbTotProcess))
    for k in keywordAll:
        nb = keywordAll[k]
        nb2 = nbTot - keywordAll[k]
        txt = "{}\t{}\t{}\n".format(k, nb, nb2)
        fileInfo.write(txt)
    fileInfo.write("\n")
    for l in languageScriptAll:
        txt = "{}\t{}\n".format(l, languageScriptAll[l])
        fileInfo.write(txt)
    
def graph(nbTools):
    tabTools = []
    for t in nbTools:
        tabTools.append([nbTools[t], t])
    tabTools.sort(reverse = True)
    x, y = [], []
    for i in range (len(tabTools)):
        x.append(tabTools[i][1])
        y.append(tabTools[i][0])

    fig, ax = plt.subplots()
    chart = sns.barplot(x=x, y=y, palette="rocket")
    chart.set_xticklabels(chart.get_xticklabels(), rotation=90, size=5)
    plt.savefig("nextflowTools.png")

if __name__ == "__main__":
    print("--------------------------Start----------------------")
    #Browse the crawler result
    crawler = "/home/clemence/FAC/Master/M1/S1/TER/AnalyseDonneesNextflow/Scripts/wf_crawl_nextflow.json"
    with open(crawler) as mon_fichier:
        data = json.load(mon_fichier)

    print(bold_color.BOLD + bold_color.RED+"CREATE DICO"+bold_color.END)
    dicoWf = createDicoWfN(data)

    #ANALYSE
    os.chdir("../Analyse")
    print(bold_color.BOLD + bold_color.RED+"ANALYSE"+bold_color.END)
    print(bold_color.BLUE + "Analyse Process" + bold_color.END)
    analysePartProcess(dicoWf)
    
    print(bold_color.BLUE + "Preparation Tools and Annotations" + bold_color.END)
    nbToolsPerWf = extractToolsAnnotations(dicoWf)
    print(nbToolsPerWf)
    print(bold_color.BLUE + "Draw Graphs" + bold_color.END)
    graph(nbToolsPerWf)
    

    print("--------------------------End----------------------")