from wfNextflow import *
import os
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
import numpy as np
import json
import pandas as pd
import time
import graphviz
from pyvis.network import Network

from sknetwork.data import convert_edge_list
from sknetwork.visualization import svg_graph
import squarify 
import matplotlib

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
    """
    Browse a json file and analyse the different workflows 
    and add in a dictionary those we do not have any errors
    """
    currentPath = os.getcwd()        
    dicoWf= {}
    nbWf = len(data.keys()) -1 #del the last which is 'last_date'
    idx = 1
    notNow = []
    for bigNames in data: 
        if bigNames != 'last_date':
            print("WORKFLOW : ", idx , "/", nbWf, " : ", bigNames)
            idx +=1
            #Collect informations
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

            #Try to go in the good directory and if does not exist create it
            nameFolder = bigNames.replace("/", "_")
            os.chdir(currentPath)
            try :
                os.chdir("../Workflows/bddFiles/" + bigNames)
            except:
                os.chdir("../Workflows/bddFiles")
                os.makedirs(bigNames, exist_ok=True)
                os.chdir(currentPath)
                os.chdir("../Workflows/bddFiles/" + bigNames)

            #Create an instance of this workflow with all the informations
            wfN = Nextflow_WF(url, files, name, nameFolder, creation_date, actual_date, last_push, owner, description, forks, stars)
            ok = wfN.extract()
            #If no problem : add to the dictionnary
            if ok:
                dicoWf.update({bigNames : wfN})
            #Else can't analyse it
            else:
                print("Can't study for the moment")
    os.chdir(currentPath)   
    return dicoWf

#-------------------------------------------------#
def extractTools(dicoWf, part):
    """
    Return all the tools and their numbers used in all the workflows present in he dictionary
    """
    nbTools = {}
    for wfn in dicoWf:
        wf = dicoWf[wfn]
        #A tool is only counted once in a workflow even if it used several times in different processes
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
    #Create the return and save informations in a file
    nbToolsPerWf = {}
    fileTools = open("nextflowTools.txt", "w")
    fileTools.write("toolname\twf_nb\n")
    for k, v in sorted(nbTools.items(), key=lambda x: x[1], reverse=True):
        nbToolsPerWf.update({k:v})
        fileTools.write(k + " : " + str(v) + "\n")
    fileTools.close()
    return nbToolsPerWf

#-------------------------------------------------#
def allLanguage(dico):
    """
    All the language of all the workklows if we could analysed it (with and without bio.tools)
    """
    file = open("language.csv", "w")
    file.write("All the Language used in all the Workflows used for the analysed or not\n\n")
    languageScript = {}
    languageStub = {}
    sumTotal = 0 
    for wfn in dico:
        wf = dico[wfn]
        dicoProcess = wf.getProcess()
        for name in dicoProcess:
            sumTotal += 1
            script = dicoProcess[name].getScript()
            if script != None:
                l = script.getLanguage()
                if l in languageScript:
                    languageScript[l] +=1
                else:
                    languageScript.update({l: 1})
            stub = dicoProcess[name].getStub()
            if stub != None:
                l = stub.getLanguage()
                if l in languageStub:
                    languageStub[l] +=1
                else:
                    languageStub.update({l: 1})
    string = "Number of process : " + str(sumTotal) + "\n\n"
    file.write(string)
    file.write("Language Script : \n")
    for l in languageScript:
        txt = "{}\t{}\n".format(l, languageScript[l])
        file.write(txt)
    file.write("\n")
    file.write("Language Stub : \n")
    for l in languageStub:
        txt = "{}\t{}\n".format(l, languageStub[l])
        file.write(txt)
    file.close()

#-------------------------------------------------#
def analysePartProcess(dicoWf):
    """
    Save all the informations about the different Workflows analysed in different files
    One file : a 'big' summary
    One file for each workflow : a 'little' summary
    """
    fileInfo = open("InfoWfNextflow/statPartsAll.csv", "w")
    txt = "Database workflow size : {}\n".format(len(dicoWf))
    fileInfo.write(txt)
    txt = "\tPresent\tNot Present\n"
    fileInfo.write(txt)
    keywordAll = {'directives':0, 'input':0, 'output':0, 'when':0, 'script':0, 'stub':0}
    languageScriptAll = {}
    languageStubAll = {}
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
        fileInfoWf.close()

    fileInfo.write("Numbers of process : {}\n".format(nbTotProcess))
    for k in keywordAll:
        nb = keywordAll[k]
        nb2 = nbTotProcess - keywordAll[k]
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
    fileInfo.close()

#-------------------------------------------------#  
def graphTools(nbTools, nbWf, histx):
    """
    Draw a histogram of the tools used
    """
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
    plt.close()

    #*********************************#
    fileTools = open('nextflowTools.txt', 'r')
    lines = fileTools.readlines()
    dicoNum = {}
    sumTotal = 0
    for i in range (1,len(lines)):
        line = lines[i].split()
        num = line[-1]
        if num in dicoNum:
            dicoNum[num] +=1
            sumTotal +=1
        else:
            dicoNum.update({num:1})
            sumTotal +=1
    fileTools.close()
    x = histx
    y = []
    yn = []
    for i in range (len(x)):
        numbers = x[i]
        dash = numbers.find('-')
        if i == len(x)-1:
            cpt = 0
            end = int(numbers[numbers.find('>=')+len('>='):])
            for n in dicoNum:
                nb = int(n)
                if nb >= end:
                    cpt +=dicoNum[n]
            y.append(cpt*100/sumTotal)
            yn.append(cpt)
        elif dash != -1:
            cpt = 0
            one = int(numbers[0:dash])
            two = int(numbers[dash+len('-'):])
            for n in dicoNum:
                nb = int(n)
                if nb>=one and nb <= two:
                    cpt +=dicoNum[n]
            y.append(cpt*100/sumTotal)
            yn.append(cpt)          
        else:
            val = 0
            cpt = 0
            num = int(numbers)
            for n in dicoNum:
                nb = int(n)
                if nb == num:
                    val = dicoNum[n]*100/sumTotal
                    cpt = dicoNum[n]
            y.append(val)
            yn.append(cpt)
            
    fig, ax = plt.subplots()
    chart = sns.barplot(x=x, y=y,palette="rocket")
    chart.set_xticklabels(chart.get_xticklabels(), size=8)
    plt.xlabel("Numbers of workflows")
    plt.ylabel("Percent of tools")
    plt.title("Distribution of the {} tools in a database composed of {} workflows".format(sumTotal,nbWf))
    i = 0
    for bar in chart.patches: 
        plt.annotate(yn[i],  
                    (bar.get_x() + bar.get_width() / 2,  
                        bar.get_height()), ha='center', va='center', 
                    size=8, xytext=(0, 5), 
                    textcoords='offset points')
        i +=1
    plt.savefig("Histogram.png")
    plt.close()

#-------------------------------------------------#  
def extractAnnotations(dicoWf, part):
    """
    Extract the annotations of each workflow (no duplication)
    After going to help to create summary 
    """
    dicoAnnot = {}
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
        dicoAnnot.update({name : tabAnnot})
    return dicoAnnot      

#-------------------------------------------------#  
def createPandaFrame(annotations):
    """
    Create a PandaFrame with statistic about tools
    Save it in a csv file
    """
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

#-------------------------------------------------#
def graphAnnotations(pandaFrame):
    """
    Histogram of all the informations contain in the pandaFrame (tools)
    """
    fig, ax = plt.subplots()
    chart = sns.countplot(x="nbOperations", data=pandaFrame)
    plt.savefig("annotationsNbOperations.png")
    plt.close()
    fig, ax = plt.subplots()
    chart = sns.countplot(x="nbInputs", data=pandaFrame)
    plt.savefig("annotationsNbInputs.png")
    plt.close()
    fig, ax = plt.subplots()
    chart = sns.countplot(x="nbOutputs", data=pandaFrame)
    plt.savefig("annotationsNbOutputs.png")
    plt.close()
    fig, ax = plt.subplots()
    chart = sns.countplot(x="nbTopics", data=pandaFrame)
    plt.savefig("annotationsNbTopics.png") 
    plt.close()

#-------------------------------------------------#
def whyNoTools(dicoWf, part):
    """
    Create a file with all the script with no tools to see and understand why there is no tools
    """
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
                infoTools = work.getAnnotations()
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
    fileInfo.close()

#-------------------------------------------------#
def graphNetwork(dico, tabEdge):    
    print(bold_color.BLUE + "CREATION NETWORKS" + bold_color.END)
    tabTools = []
    idx = 0
    file = open("Networks/0_NumbersNameCorrespondence.txt", "w")
    fileb = open("listTools.txt", "w")
    #Creation of a tab : idx + name of the wf + list of tools used in this wf
    for k in dico:
        annot = dico[k].getAnnotationsScript()
        tools = []
        for a in annot:
            if not annot[a]['name'] in tools:
                tools.append(annot[a]['name'])
        tabTools.append([idx, k, tools])
        string = str(idx) + " : " + k + "\n"
        file.write(string)
        string ="\t" + str(idx) + ' - ' +  k + " :\n"
        fileb.write(string)
        string = str(tools) + "\n\n"
        fileb.write(string)
        idx +=1
    file.close()
    fileb.close()

    #Creation of a tab : idx wf 1 + idx wf 2 + numbers of shared tools 
    tabComparison = []
    for i in range(len(tabTools)):
        toolsOne = tabTools[i][2]
        for j in range(i+1,len(tabTools)):
            nbCommon = 0
            toolsTwo = tabTools[j][2]
            for t in toolsTwo:
                if t in toolsOne:
                    nbCommon +=1
            tabComparison.append([i, j, nbCommon])

    node = [[] for _ in range(len(tabEdge))]
    edge = [[] for _ in range(len(tabEdge))]
    
    for i in range(len(tabComparison)):
        dejavu = []
        nbSame = tabComparison[i][2]
        for j in range (len(tabEdge)-1,-1,-1):
            if not j in dejavu :
                if nbSame >= tabEdge[j]:
                    for k in range (j,-1,-1):
                        one = str(tabComparison[i][0])
                        two = str(tabComparison[i][1])
                        edge[k].append((one,two))
                        if not one in node[k]:
                                  node[k].append(one)
                        if not two in node[k]:
                                  node[k].append(two)
                        dejavu.append(k)

    for i in range (len(tabEdge)):
        print("Network :", str(i+1) , " / ", str(len(tabEdge)))
        if len(node[i]) != 0:
            name = 'Networks/graphviz_network_' + str(tabEdge[i]) + '.gv'  
            g = graphviz.Graph(filename=name, engine='sfdp', format='png', \
                                node_attr={'color': 'orangered1', 'style': 'filled', 'shape':'oval'}) 
            
            for j in range (len(edge[i])):
                g.edge(edge[i][j][0], edge[i][j][1])
            g.render()
            g.save()

            #Create a file with stat 
            string = "Networks/" + str(tabEdge[i]) + "_network.txt"
            file = open(string, "w")
            string = "Network with a edge bewteen two nodes if less " + str(tabEdge[i]) +  " shared tools :\n\n"
            file.write(string)
            #Nb edge
            string = "Numbers of Nodes : " + str(len(node[i])) + "\n\n"
            file.write(string)
            #Nb node
            string = "Numbers of Edges : " + str(len(edge[i])) + "\n\n"
            file.write(string)
            string = "List of the edges : \n"
            file.write(string)
            for j in range (len(edge[i])):
                one = str(edge[i][j][0])
                two = str(edge[i][j][1])
                string = one + " -- " + two + "\n"
                file.write(string)
            file.close()


            #Interactif networks
            """g2 = nx.Graph()
            g2.add_nodes_from(node[i])
            g2.add_edges_from(edge[i])
            
            net = Network('100%', '100%')
            net.from_nx(g2)
            name = 'Networks/pyvisnetwork' + str(tabEdge[i]) + '.html'
            net.show_buttons(filter_=['physics'])
            net.save_graph(name)
            """
            graph = convert_edge_list(edge[i])
            adjacency = graph.adjacency
            names = graph.names
            name = 'Networks/scikit_network' + str(tabEdge[i]) + '.png'
            _ = svg_graph(adjacency, names=names,node_color='#f95548',edge_color='#4bafde',node_size=2.5, filename= name)

#-------------------------------------------------#
def graphTopics(dico):
    file = open('Topics/listAnnotTopic.txt', "w")
    fileb = open('Topics/listAnnotTopic2.txt', "w")
    dejaVubis = []
    dejaVu3 = []
    data = pd.DataFrame(columns=['name', 'uri', 'topic', 'function'])

    for wfn in dico :
        wf = dico[wfn]
        annot = wf.getAnnotationsScript()
        string = "\n\t" + wfn + " : \n"
        file.write(string)
        for a in annot:
            name = annot[a]['name']
            if not name in dejaVubis:
                dejaVubis.append(name)
                tabT = annot[a]['topic'][0]
                string = name + " : \n" + str(tabT) + "\n\n"
                fileb.write(string)

            if not name in dejaVu3:
                dejaVu3.append(name)
                uri = annot[a]['uri']
                topic = annot[a]['topic']
                function = annot[a]['function']
                data = data.append({'name':name, 'uri':uri, 'topic':topic, 'function':function}, ignore_index=True) 
    data.to_csv("toolsAnnot.csv", index=False)
    file.close()
    fileb.close()

#-------------------------------------------------#
def analysePart(part, dico):
    """
    Global functions to analyse Script or Stub
    """
    #Go in the good directory
    try:
        os.chdir(part)
    except:
        os.makedirs(part, exist_ok=True)
        os.chdir(part)

    print(bold_color.BOLD + bold_color.RED+"ANALYSE "+ part +bold_color.END)    
    print(bold_color.BLUE + "Preparation Tools" + bold_color.END)
    nbToolsPerWf = extractTools(dico, part)
    print(nbToolsPerWf)
    if len(nbToolsPerWf) != 0:
        print(bold_color.BLUE + "Draw Graphs Tools" + bold_color.END)
        print(bold_color.BLUE + "Tool Histogram" + bold_color.END)
        if part == 'stub':
            histx = ["1", "2","3","4","5", '>6'] 
        else:
            histx = ["1", "2","3","4","5", '6', "7-9", "10-24", '25-49', "50-99", ">=100"]
        graphTools(nbToolsPerWf, len(dico), histx)

        print(bold_color.BLUE + "Preparation Annotations" + bold_color.END)
        annotations = extractAnnotations(dico, part)
        print(bold_color.BLUE + "Creation Stat Annotations" + bold_color.END)
        stat = createPandaFrame(annotations)
        print(stat)
        print(bold_color.BLUE + "Draw Graphs Annotations" + bold_color.END)
        graphAnnotations(stat)

    print(bold_color.BLUE + "Why No Tools" + bold_color.END)
    whyNoTools(dicoWf, part)
    os.chdir("../")

#-------------------------------------------------#
def whichWithTools(dicoWf):
    """
    Create a new dictionary with all the workflows which contain less one bio.tools
    """
    perfect = 0
    newDicoWf = {}
    for wfn in dicoWf:
        npProcessScriptWithAnnotations = 0
        nbProcessScript = 0
        npProcessStubWithAnnotations = 0
        nbProcessStub = 0
        wf = dicoWf[wfn]
        dicoProcess = wf.getProcess()
        for name in dicoProcess:
            script = dicoProcess[name].getScript()
            if script != None:
                nbProcessScript += 1 
                scriptTools = script.getAnnotations()
                if len(scriptTools) > 0:
                    npProcessScriptWithAnnotations +=1
            
            stub = dicoProcess[name].getStub()
            if stub != None:
                nbProcessStub += 1 
                stubTools = stub.getAnnotations()
                if len(stubTools) > 0: 
                    npProcessStubWithAnnotations += 1

        if script != None and stub != None:
            if npProcessScriptWithAnnotations != 0 or npProcessStubWithAnnotations != 0: #or or and ??
                perfect += 1
                newDicoWf.update({wfn: wf})
        elif script != None and stub == None:
            if npProcessScriptWithAnnotations != 0:
                perfect += 1
                newDicoWf.update({wfn: wf})
        elif script == None and stub != None:
            if npProcessStubWithAnnotations != 0:
                perfect += 1
                newDicoWf.update({wfn: wf})

    percent = (perfect/len(dicoWf))*100
    print(bold_color.BOLD + "Numbers with less one Bio.tools : " + str(perfect) + "/"+str(len(dicoWf)) + " soit " + str(percent) + "%" +  bold_color.END)
    
    return newDicoWf

"""
Main Part - Analyse All the Workflow in the json file
"""
if __name__ == "__main__":
    startTime = time.time()
    print(bold_color.YELLOW + "--------------------------Start----------------------"+bold_color.END)
    currentPath = os.getcwd()

    #Create folders if don't exist
    try:
        os.chdir("../Workflows/bddFiles/")
    except:
        os.chdir("../")
        os.makedirs("Workflows/bddFiles", exist_ok=True)
    os.chdir(currentPath)

    #Browse the crawler result
    crawler = "/home/clemence/FAC/Master/M1/TER/AnalyseDonneesNextflow/Scripts/wf_crawl_nextflow.json"
    with open(crawler) as mon_fichier:
        data = json.load(mon_fichier)
    #Creation of the first dictionary with all the workflows we can analyse for the moment 
    print(bold_color.BOLD + bold_color.RED+"CREATE DICO"+bold_color.END)
    dicoWf = createDicoWfN(data)
    print(bold_color.BOLD + "Can analyse : ", str(len(dicoWf)) , "/", str(len(data)-1)+bold_color.END)

    print(bold_color.BOLD + bold_color.RED+"INFO ON TOOLS AND WORKFLOW"+bold_color.END)
    #Creation of a new dictionary with all the workflows we can analyse and include less one Bio.tools 
    newDicoWf = whichWithTools(dicoWf)

    percent2 = len(newDicoWf)/((len(data)-1))*100
    print(bold_color.BOLD + "FINAL : ", str(percent2) , "% of all the Worflows would be analyse !" + bold_color.END)

    #ANALYSE
    #Create folders if don't exist
    folder = ['stub', 'script', 'InfoWfNextflow', 'Networks', 'Topics']
    try:
        os.chdir("../Analyse")
    except:
        os.chdir("../")
        os.makedirs("Analyse/stub", exist_ok=True)
        os.makedirs("Analyse/script", exist_ok=True)
        os.makedirs("Analyse/InfoWfNextflow", exist_ok=True)
        os.makedirs("Analyse/Networks", exist_ok=True)
        os.makedirs("Analyse/Topics", exist_ok=True)
        os.chdir("Analyse")
    analyse = os.getcwd()

    for f in folder:
        try:
            os.chdir(f)
        except:
            os.makedirs(f, exist_ok=True)	
        os.chdir(analyse)
    
    print(bold_color.BOLD + bold_color.RED + "ANALYSE GLOBAL ON " + str(len(newDicoWf)) + bold_color.END)
    #Analyse the Process of the different Workflows
    analysePartProcess(newDicoWf)
    #Stat language
    print(bold_color.BOLD + bold_color.RED + "Stat global on language" + bold_color.END)
    allLanguage(dicoWf)
    #Create Networks
    print(bold_color.BOLD + bold_color.RED + "Network Graphs" + bold_color.END)
    graphNetwork(newDicoWf,[1,2,3,5])
    #Analyse the tools most used in the workflows
    analysePart('script', newDicoWf)
    analysePart('stub', newDicoWf)
    #Analyse Topic
    print(bold_color.BOLD + bold_color.RED + "Topic Graphs" + bold_color.END)
    graphTopics(newDicoWf)

    finalTime = str((time.time() - startTime)/60)
    print(bold_color.BOLD + "Execution Time :" + bold_color.END + finalTime +" min")
    print(bold_color.YELLOW +"--------------------------End----------------------"+bold_color.END)