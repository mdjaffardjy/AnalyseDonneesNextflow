from wfNextflow import *
import os
import matplotlib.pyplot as plt
import seaborn as sns
import json
import pandas as pd
import time

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
        try :
            os.chdir("../Workflows/bddFiles/" + bigNames)
        except:
            os.chdir("../Workflows/bddFiles")
            #os.system("mkdir " + nameFolder)
            #os.chdir(currentPath)
            #os.chdir("../Workflows/bddFiles/" + nameFolder)
            os.makedirs(bigNames, exist_ok=True)
            os.chdir(currentPath)
            os.chdir("../Workflows/bddFiles/" + bigNames)

        wfN = Nextflow_WF(url, files, name, nameFolder, creation_date, actual_date, last_push, owner, description, forks, stars)
        wfN.extract()
        dicoWf.update({bigNames : wfN})
    os.chdir(currentPath)   
    return dicoWf

def extractTools(dicoWf, part):
    nbTools = {}
    for wfn in dicoWf:
        wf = dicoWf[wfn]
        dejaVu = []
        if part == 'script':
            tools = wf.getAnnotationsScript()
        elif part == 'stub':
            tools = wf.getAnnotationsStub()
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
    fileTools.write("toolname\twf_nb\n")
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
    languageStubAll = {}
    nbTot = 0
    nbTotProcess = 0
    for wfn in dicoWf:
        wf = dicoWf[wfn]
        string = "InfoWfNextflow/statParts_" + wf.getNameFolder()+ ".csv"
        keyword = {'directives':0, 'input':0, 'output':0, 'when':0, 'script':0, 'stub':0}
        languageScript = {}
        languageStub = {}
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
                
                if k == 'stub'and part != None:
                    l = part.getLanguage()
                    if l in languageStub:
                        languageStub[l] +=1
                    else:
                        languageStub.update({l: 1})
                        
                    if l in languageStubAll:
                        languageStubAll[l] +=1
                    else :
                        languageStubAll.update({l: 1})


        for k in keyword:
            nb = keyword[k]
            nb2 = len(dicoProcess) - keyword[k]
            txt = "{}\t{}\t{}\n".format(k, nb, nb2)
            fileInfoWf.write(txt)
        fileInfoWf.write("\n")
        fileInfoWf.write("Language Script :\n")
        for l in languageScript:
            txt = "{}\t{}\n".format(l, languageScript[l])
            fileInfoWf.write(txt)
        fileInfoWf.write("\n")
        fileInfoWf.write("Language Stub :\n")
        for l in languageStub:
            txt = "{}\t{}\n".format(l, languageStub[l])
            fileInfoWf.write(txt)
        """for _ in range (3):
            fileInfoWf.write("\n")"""
    
    fileInfo.write("Numbers of process : {}\n".format(nbTotProcess))
    for k in keywordAll:
        nb = keywordAll[k]
        nb2 = nbTot - keywordAll[k]
        txt = "{}\t{}\t{}\n".format(k, nb, nb2)
        fileInfo.write(txt)
    fileInfo.write("\n\n")
    fileInfo.write("Language Script : \n")
    for l in languageScriptAll:
        txt = "{}\t{}\n".format(l, languageScriptAll[l])
        fileInfo.write(txt)
    fileInfo.write("\n")
    fileInfo.write("Language Stub : \n")
    for l in languageStubAll:
        txt = "{}\t{}\n".format(l, languageStubAll[l])
        fileInfo.write(txt)
    
def graphTools(nbTools):
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

def extractAnnotations(dicoWf, part):
    dicoAnnot = {}
    ##dicoToolsAnnot = {}
    for wfn in dicoWf:
        wf = dicoWf[wfn]
        name = wf.getNameFolder()
        tabAnnot = []
        if part == 'script':
            annot = wf.getAnnotationsScript()
        elif part == 'stub':
            annot = wf.getAnnotationsStub()
        for a in annot:
            if not annot[a] in tabAnnot:
                tabAnnot.append(annot[a])
            ##if a not in dicoToolsAnnot:
            ##    dicoToolsAnnot.update({a:annot[a]})
        dicoAnnot.update({name : tabAnnot})

    return dicoAnnot ##, dicoToolsAnnot       

def createPandaFrame(annotations):
    dfToolsStatsAnnot = pd.DataFrame(columns=["toolname","nbOperations", "nbInputs", "nbOutputs", "nbTopics"])
    dejaVu = []
    for a in annotations:
        for i in range (len(annotations[a])):
                work = annotations[a][i]
                tool = work['name']
                if not tool in dejaVu:
                    dejaVu.append(tool)
                    if len(work['function']) >0 :
                        nbOpe = len(work["function"][0]["operation"][0])
                        nbInput = len(work["function"][0]["input"])
                        nbOutput = len(work["function"][0]["output"])
                    else:
                        nbOpe = 0
                        nbInput = 0
                        nbOutput = 0
                    nbTopics = len(work["topic"][0])
                    dfToolsStatsAnnot = dfToolsStatsAnnot.append({"toolname": tool, "nbOperations":nbOpe, "nbInputs":nbInput, "nbOutputs":nbOutput, "nbTopics":nbTopics}, ignore_index=True)
    dfToolsStatsAnnot.to_csv("statAnnotations.csv",index=False)  
    return dfToolsStatsAnnot

"""def get_df_stats_annot(dict_tools):
    #ne prend pas en compte les synonymes
    df_tools_stats_annot = pd.DataFrame(columns=["toolname",
                                                 "tool_id",
                                                 "nb_operations",
                                                 "nb_inputs",
                                                 "nb_outputs",
                                                 "nb_topics"])

    for tool in dict_tools: #TODO : unicité ? dict tools plus gd que tot tools
        # print(tool)
        if len(dict_tools[tool]["function"]) > 0:
            nb_operations = len(dict_tools[tool]["function"][0]["operation"][0])
            nb_inputs = len(dict_tools[tool]["function"][0]["input"])
            nb_outputs = len(dict_tools[tool]["function"][0]["output"])
        else:
            nb_operations = 0
            nb_inputs = 0
            nb_outputs = 0
        nb_topics = len(dict_tools[tool]["topic"][0])
        df_tools_stats_annot = df_tools_stats_annot.append({"toolname": tool,
                                                            "tool_id" : dict_tools[tool]["name"],
                                                            "nb_operations": nb_operations,
                                                            "nb_inputs": nb_inputs,
                                                            "nb_outputs": nb_outputs,
                                                            "nb_topics": nb_topics}, ignore_index=True)
    df_tools_stats_annot.to_csv("statAnnotations2.csv",index=False)  
    return df_tools_stats_annot """  

def whyNoTools(dicoWf, part):
    string = "whyNo_" + part + ".txt"
    fileInfo = open(string, "w")
    for wfn in dicoWf:
        writeName = True
        wf = dicoWf[wfn]
        nameWf = "\t\t" + wf.getNameFolder()
        dicoProcess = wf.getProcess()
        for name in dicoProcess:
            if part == 'script':
                work = dicoProcess[name].getScript()
            elif part == 'stub': 
                work = dicoProcess[name].getStub()
            
            if work != None:
                infoTools = work.getTools()
                if len(infoTools) == 0:
                    if writeName:
                        fileInfo.write(nameWf + " ::\n")
                        writeName = False
                    string = name + " :\n"
                    fileInfo.write(string)
                    if work.getLanguage() == 'bash':
                        string = work.getString() + "\n"
                    else:
                        string = "Language used : " + work.getLanguage() + "\n"
                    fileInfo.write(string)
                    fileInfo.write("\n")

def graphAnnotations(pandaFrame):
    fig, ax = plt.subplots()
    chart = sns.countplot(x="nbOperations", data=pandaFrame)
    plt.savefig("annotationsNbOperations.png")
    fig, ax = plt.subplots()
    chart = sns.countplot(x="nbInputs", data=pandaFrame)
    plt.savefig("annotationsNbInputs.png")
    fig, ax = plt.subplots()
    chart = sns.countplot(x="nbOutputs", data=pandaFrame)
    plt.savefig("annotationsNbOutputs.png")
    fig, ax = plt.subplots()
    chart = sns.countplot(x="nbTopics", data=pandaFrame)
    plt.savefig("annotationsNbTopics.png") 
    

def analysePart(part):
    try:
        os.chdir(part)
    except:
        os.makedirs(part, exist_ok=True)
        os.chdir(part)

    print(bold_color.BOLD + bold_color.RED+"ANALYSE "+ part +bold_color.END)    
    print(bold_color.BLUE + "Preparation Tools" + bold_color.END)
    nbToolsPerWf = extractTools(dicoWf, part)
    print(nbToolsPerWf)
    if len(nbToolsPerWf) != 0:
        print(bold_color.BLUE + "Draw Graphs Tools" + bold_color.END)
        graphTools(nbToolsPerWf)

        print(bold_color.BLUE + "Preparation Annotations" + bold_color.END)
        annotations = extractAnnotations(dicoWf, part)  ##, dicoToolsAnnot
        print(bold_color.BLUE + "Creation Stat Annotations" + bold_color.END)
        stat = createPandaFrame(annotations)
        print(stat)
        print(bold_color.BLUE + "Draw Graphs Annotations" + bold_color.END)
        graphAnnotations(stat)

    ##stat2 = get_df_stats_annot(dicoToolsAnnot)
    print(bold_color.BLUE + "Why No Tools" + bold_color.END)
    whyNoTools(dicoWf, part)
    os.chdir("../")


if __name__ == "__main__":
    startTime = time.time()
    print(bold_color.YELLOW + "--------------------------Start----------------------"+bold_color.END)
    currentPath = os.getcwd()
    #Browse the crawler result
    crawler = "/home/clemence/FAC/Master/M1/S1/TER/AnalyseDonneesNextflow/Scripts/wf_crawl_nextflow_petit.json"
    with open(crawler) as mon_fichier:
        data = json.load(mon_fichier)

    print(bold_color.BOLD + bold_color.RED+"CREATE DICO"+bold_color.END)
    dicoWf = createDicoWfN(data)
    
    #ANALYSE
    try:
        os.chdir("../Analyse")
    except: 
        os.chdir("../")
        os.makedirs("Analyse/stub", exist_ok=True)
        os.makedirs("Analyse/script", exist_ok=True)
        os.makedirs("Analyse/InfoWfNextflow", exist_ok=True)
        os.chdir("../Analyse")

    print(bold_color.BOLD + bold_color.RED + "ANALYSE GLOBAL" + bold_color.END)
    analysePartProcess(dicoWf)

    #os.chdir(currentPath)
    analysePart('script')
    #os.chdir(currentPath)
    analysePart('stub')
 
    finalTime = str((time.time() - startTime)/60)
    print(bold_color.BOLD + "Execution Time :" + bold_color.END + finalTime +" min")
    print(bold_color.YELLOW +"--------------------------End----------------------"+bold_color.END)
