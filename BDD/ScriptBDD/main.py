# Nextflow Analyzer
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022

from pathlib import Path
from .bdd_connexion import *
import argparse
import json 
import os

 
print('''
     _    ____   ____     ____  ____   ____
    / \  |  _ \ |  _ \   |    \|  _ \ |  _ \     |
   / _ \ | | \ \| | \ \  |    /| | \ \| | \ \    |
  / ___ \| |_/ /| |_/ /  |    \| |_/ /| |_/ /    |
 /_/   \_|____/ |____/   |____/|____/ |____/     .

''')

print("""________________________________________________

Developped by Clemence Sebe and George Marchment
________________________________________________\n""")

def main():
    #Get current directory
    current_directory = os.getcwd()

    parser = argparse.ArgumentParser()
    #Obligatory
    parser.add_argument('--system', default='')  #S ou N for Snakemake or Nextflow
    parser.add_argument('--results_directory', default='') #where are the results files
    parser.add_argument('--json_directory', default = '')    #where are the json with all the informaiton on the wf and the authors
    args = parser.parse_args() 

    if args.system == '' :
        raise Exception('\x1b[1;37;41m' + f'The parameter "system" was not given!!'+ '\x1b[0m')
    if args.results_directory == '':
        raise Exception('\x1b[1;37;41m' + f'The parameter "results_directory" was not given!!'+ '\x1b[0m')
    if args.json_directory == '':
        raise Exception('\x1b[1;37;41m' + f'The parameter "json_directory" was not given!!'+ '\x1b[0m')


    #give in input the fold where we can find the 2 different json:
    #each json must contain the word : wf or author
    tabAdressJsonGlobalInfo = ['_','_']
    tabWords = ['wf', 'author']
    for p in Path(args.json_directory).iterdir():
        if p.is_file():
            s = str(p)
            s2 = s.split('/')[-1]
            for w in tabWords:
                if s2.find(w) != -1 and w == 'wf':
                    tabAdressJsonGlobalInfo[0] = s
                elif s2.find(w) != -1 and w == 'author':
                    tabAdressJsonGlobalInfo[1] = s
    for i in range (len(tabAdressJsonGlobalInfo)):
        if tabAdressJsonGlobalInfo[i] == '_':
            raise Exception ("One file is missing : " + tabWords[i])

    #Setting the current directory where the results are
    os.chdir(args.results_directory)

    #creeate the dico for save the workflow and after calcul the similarity
    dicoAllProcess = {}

    #Création d'un tableau avec toutes les adresses des dossiers dans lequel on a eu des résultats (au moins 1 process)
    #On ne met pas dans la base ceux qui n'ont aucun process
    listDirectoryResults = []
    simRepository = args.results_directory + "/Results_Similarity"
    for (directory, underDirectory, fichiers) in os.walk(args.results_directory):
        if underDirectory == [] and len(fichiers) != 0:
            if directory != simRepository:
                listDirectoryResults.append(directory)


    #attention : ne pas mettre ceux avec 0 d'outils - on garde seulement ceux avec au minimum un outil ds le wf
    wfNoTools = []

    for i in range (len(listDirectoryResults)):
        nameWf = listDirectoryResults[i].replace(args.results_directory + '/', '')
        temp = list(nameWf)
        idx = temp.index('_')
        temp[idx] = '/'
        nameWf = "".join(temp)
   
        print(str(i+1) + "/" + str(len(listDirectoryResults)) + " : " + nameWf)

        os.chdir(listDirectoryResults[i])
        listFile = os.listdir(listDirectoryResults[i])

        # pour savoir si on travaille sur un wf Nextflow ecrit en dsl1 ou 2 car on a la structure que pour dsl1
        #si le wf est ecrit en dsl2 on obtient qu'un fichier resultat avec les process extraits
        if args.system == 'N' and len(listFile) == 1: 
            dsl = 2
        #sinon on obtient plusieurs fichiers car on a aussi pu extraire les channels et la structure
        elif args.system == 'N' and len(listFile) > 1:
            dsl = 1
        else:
            dsl = 0 #snakemake
        

        with open('processes_info.json') as process_json:
            processes = json.load(process_json)
        
        #Check if we have less one tool in this workflow
        nbTools = 0
        for nameProcess in processes:
            tools = processes[nameProcess]['tools']
            nbTools += len(tools)
        
        if nbTools != 0:
            #add in the Database
            dicoAllProcess = addInDatabase(tabAdressJsonGlobalInfo, nameWf, dsl, dicoAllProcess)
        else:
            wfNoTools.append(nameWf)
            #print('No tools in this workflow : don\'t add in the database\n')

    '''os.chdir(args.results_directory)
    with open("allProcesses.json", 'w') as dicoP:
        json.dump(dicoAllProcess, dicoP, indent=4)'''

    os.chdir(current_directory)

    fileWfNoTools = open('summary.txt', 'w')
    s = f"On {len(listDirectoryResults)}, {len(listDirectoryResults) - len(wfNoTools)} add in the database \n"
    s += "Numbers of wf without any tools : "  + str(len(wfNoTools)) + '\n\n'
    fileWfNoTools.write(s)
    """s = ""
    for w in wfNoTools:
        s+= w + '\n'
    fileWfNoTools.write(s)"""
    fileWfNoTools.close()

    print(f"\nOn {len(listDirectoryResults)}, {len(listDirectoryResults) - len(wfNoTools)} add in the database")
