from wfNextflow import *
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":
    print("--------------------------Start----------------------")
    path = "/home/clemence/FAC/Master/M1/S1/TER/AnalyseDonneesNextflow/Workflows/Tuto_Nextflow/bddProcess2/*.nf"
    bddProcess = glob.glob(path, recursive= True)
    print("Taille de la bdd :", len(bddProcess))
    currentPath = os.getcwd() 

    print("Separate the different wf")
    dicoWf= {}
    for i in range (len(bddProcess)):
        f = open(bddProcess[i],"r")
        url = f.readlines()[0].strip() #give the url of the wf
        if url in dicoWf:
            dicoWf[url].append(bddProcess[i]) 
        else:
            dicoWf.update({url:[bddProcess[i]]})

        f.close()

    nb = 0
    for b in dicoWf:
        nb += len(dicoWf[b])
    #print(nb)
    assert nb == len(bddProcess)

    print("Work on the different wf")
    tabWf = []
    #idx = 0 #AIDE DEBUT A ENLEVER
    for url in dicoWf:
        #if idx == 0:
        wfN = Nextflow_WF(url, dicoWf[url])
        wfN.extract()
        tabWf.append(wfN)
        #idx +=1

    #ANALYSE
    print("Analyse")
    nbToolsPerWf = {}
    for wf in tabWf:
        dejaVu = []
        tools = wf.getAnnotations()
        for t in tools:
            tt = tools[t]['name']
            if not tt in dejaVu:
                if not  tt in nbToolsPerWf:
                    nbToolsPerWf.update({tt:1})
                else:
                    nbToolsPerWf[tt] += 1
                dejaVu.append(tt)
    print(nbToolsPerWf)

    os.chdir("/home/clemence/FAC/Master/M1/S1/TER/AnalyseDonneesNextflow/Analyse")

    tabTools = []
    for t in nbToolsPerWf:
        tabTools.append([nbToolsPerWf[t], t])
    tabTools.sort(reverse = True)
    x, y = [], []
    for i in range (len(tabTools)):
        x.append(tabTools[i][1])
        y.append(tabTools[i][0])

    fig, ax = plt.subplots()
    chart = sns.barplot(x=x, y=y, palette="rocket")
    chart.set_xticklabels(chart.get_xticklabels(), rotation=80, size=5)
    plt.savefig("nextflowTools.png")

    print("--------------------------End----------------------")