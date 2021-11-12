from process import *

import matplotlib.pyplot as plt
import os
import glob

if __name__ == "__main__":
    print("-----------------------------START-----------------------------")
    path = "/home/clemence/FAC/M1/TER/AnalyseDonneesNextflow/Workflows/Tuto_Nextflow/bddProcess"+"/**/*.nf"
    bddProcess = glob.glob(path, recursive= True)
    print("Taille de la bdd :", len(bddProcess))
    currentPath = os.getcwd() 

    languageScript = {}
    keyword = {'directives':0, 'input':0, 'output':0, 'when':0, 'script':0, 'stub':0}

    for i in range (len(bddProcess)):
        try:
            f = open(bddProcess[i],"r")
            process = f.read()
            p = Process(process) 
            p.extractProcess()
            informations = p.getAll()
            for part, k in zip(informations[1:], keyword):
                if part != None:
                    keyword[k] += 1
                if k == 'script':
                    language = part.getLanguage()
                    for l in language:
                        if l in languageScript:
                            languageScript[l] +=1
                        else:
                            languageScript.update({l: 1})
            f.close()
        except:
            print("ERROR")
            None

    os.chdir("/home/clemence/FAC/M1/TER/AnalyseDonneesNextflow/Analyse")
    #Histogram 
    for k in keyword:
        fig,ax = plt.subplots()
        val = [keyword[k], len(bddProcess)-keyword[k]]
        plt.bar(["Present", "Not Present"], val, color = ['#00429d', '#7f40a2'])
        plt.title(k)
        plt.ylabel('Number')
        name = k + ".png"
        plt.savefig(name)

    #Language
    x = []
    y = []
    for l in languageScript:
        fig,ax = plt.subplots()
        x.append(l)
        y.append(languageScript[l])
    plt.bar(x,y)  
    plt.title("Language Script")
    plt.ylabel("Number")
    plt.savefig("languageScript.png")
    os.chdir(currentPath)

    """
    adress = "/home/clemence/FAC/M1/TER/AnalyseDonneesNextflow/Workflows/Tuto_Nextflow/test.nf"
    f = open(adress,"r")
    lines = f.read()

    p = Process(lines) 
    p.extractProcess()
    p.printInformations()

    f.close()
    """
    print("-----------------------------END-----------------------------")
