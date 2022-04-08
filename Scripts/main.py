# Nextflow Analyzer
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022

import argparse
from pathlib import Path
import os
import glob2

 
print('''
  _   _ _______  _______ _____ _     _____        __     _    _   _    _    _  __   ____________ ____  
 | \ | | ____\ \/ |_   _|  ___| |   / _ \ \      / /    / \  | \ | |  / \  | | \ \ / |__  | ____|  _ \ 
 |  \| |  _|  \  /  | | | |_  | |  | | | \ \ /\ / /    / _ \ |  \| | / _ \ | |  \ V /  / /|  _| | |_) |
 | |\  | |___ /  \  | | |  _| | |__| |_| |\ V  V /    / ___ \| |\  |/ ___ \| |___| |  / /_| |___|  _ < 
 |_| \_|_____/_/\_\ |_| |_|   |_____\___/  \_/\_/    /_/   \_|_| \_/_/   \_|_____|_| /____|_____|_| \_\ 
                                                                                                       
''')

print("""________________________________________________
Developped by Clemence Sebe and George Marchment
________________________________________________\n""")

from .workflow import *
from .postgresql import *

def main():
    #Get current directory
    current_directory = os.getcwd()
    
    parser = argparse.ArgumentParser()
    #Obligatory
    parser.add_argument('input') 
    parser.add_argument('results_directory')
    parser.add_argument('json_directory')
    #Facultative
    parser.add_argument('--name', default='Workflow_Analysis')
    parser.add_argument('--mode', default='single') #single mode is the default
    parser.add_argument('--dev', default='F') #For developpeur mode or not
    args = parser.parse_args() 
    
    #Setting the current directory to where the extracted data will be saved
    os.chdir(args.results_directory)

    #give in input the fold were we can find the 3 different json:
    #each json must contain the word : wf or author or lisence
    fileInputJSON = ['_','_', '_']
    tabWords = ['wf', 'author', 'license']
    for p in Path(args.json_directory).iterdir():
        if p.is_file():
            s = str(p)
            s2 = s.split('/')[-1]
            for w in tabWords:
                if s2.find(w) != -1 and w == 'wf':
                    fileInputJSON[0] = s
                elif s2.find(w) != -1 and w == 'author':
                    fileInputJSON[1] = s
                elif s2.find(w) != -1 and w == 'license':
                    fileInputJSON[2] = s
    for i in range (len(fileInputJSON)):
        if fileInputJSON[i] == '_':
            try :
                t = 1/0
            except :
                print("Il manque un fichier : ", tabWords[i])

    #=========
    # SINGLE
    #=========
    if(args.mode == 'single'):
        print('')
        print('\x1b[1;37;42m' + 'Single Workflow analysis mode was selected' + '\x1b[0m')
        print('')
        #Checking that the file given exists
        if Path(args.input).is_file():
            #The file exists
            print(f'Analyzing the workflow : {args.input}')
            #Creating the new file if it doesn't exist
            os.system(f"mkdir -p {args.name}")
            #Setting the current directory to the file directory
            res=args.results_directory+'/'+args.name
            os.chdir(res)
            #Analysing the workflow
            w = Workflow(args.input)
            w.initialise()
            print(f'Results saved in : {res}')
            #Delete developper files if not in dev mode
            if(args.dev == 'F'):
                os.system('rm channels_extracted.nf')
                os.system('rm processes_extracted.nf')
        else:
            raise Exception('\x1b[1;37;41m' + f"Either '{args.input}' is not a file or doesn't exist!!"+ '\x1b[0m')
    
    #=========
    # MULTI
    #=========
    elif(args.mode == 'multi'):
        total, DSL2, DSL1_analyzed, DSL1_not_analyzed, curly, problem_process= 0, 0, 0, 0, 0, 0
        errors, DSL2_tab, curlies_tab, analyzed_tab, process_tab = [], [], [], [], []
        print('')
        print('\x1b[7;33;40m' + 'Multiple Workflow analysis mode was selected' + '\x1b[0m')
        print('')
        #Checking that the input is not a file
        if Path(args.input).is_file():
            raise Exception('\x1b[1;37;41m' + f"'{args.input}' is file, a directory is expected for multi mode!!"+ '\x1b[0m')
        else:
            tabWf = []
            whereIsFile = glob2.glob(args.input+'/**/*.nf')
            for i in range(len(whereIsFile)):
                whereIsFile[i] = whereIsFile[i].replace(args.input, "")
                for s in range (len(whereIsFile[i])-1, 0, -1):
                    if whereIsFile[i][s] == '/':
                        break
                whereIsFile[i] = whereIsFile[i][0:s]
                if whereIsFile[i][0] == '/':
                    whereIsFile[i] = whereIsFile[i][1:]
            
            for w in whereIsFile:
                if not w in tabWf:
                    tabWf.append(w)

            for i in range (len(tabWf)):
                total += 1
                print(f'{i+1}/{len(tabWf)}')
                print(f'Analyzing the workflow : {tabWf[i]}')
                #Creating the new folder to save the data from the analyze
                res=args.results_directory+'/'+args.name+'/'+tabWf[i]
                os.system(f"mkdir -p {res}")
                os.chdir(res)
                #Analysing the workflow
                try:
                    folder = args.input + "/" + tabWf[i] 
                    nbFile = 0
                    file = []
                    for p in Path(folder).iterdir():
                        if p.is_file():
                            nbFile += 1
                            file.append(p)
                    if nbFile == 1:
                        w = Workflow(file[0])
                        w.initialise()
                        DSL1_analyzed+=1
                        analyzed_tab.append(tabWf[i])
                        #add into the database                    
                        addInDatabase(fileInputJSON, tabWf[i], args.json_directory)
                        #Delete developper files if in dev mode
                        if(args.dev != 'F'):
                            os.system('rm channels_extracted.nf')
                            os.system('rm processes_extracted.nf')
                    else :
                        raise Exception("Workflow written in DSL2 : I don't know how to analyze the workflow yet") 

                except Exception as inst:
                    #Error DSL2
                    if (str(inst) == "Workflow written in DSL2 : I don't know how to analyze the workflow yet"):
                        print('\x1b[1;37;44m' + f"Workflow written in DSL2 : I don't know how to analyze the workflow yet"+ '\x1b[0m')
                        DSL2+=1
                        DSL2_tab.append(tabWf[i])
                        """try:
                            folder = args.input + "/" + tabWf[i] 
                            nbFile = 0
                            files = []
                            for p in Path(folder).iterdir():
                                if p.is_file():
                                    nbFile += 1
                                    files.append(p)
                            k = 0
                            for f in files:    
                                p = Workflow(f)
                                p.initialise_main()
                                addInDatabase(fileInputJSON, tabWf[i], args.json_directory)
                                listFile = Path(os.getcwd()).iterdir()
                                for f in listFile:
                                    if f.is_file():
                                        nameFile = str(f).split('/')[-1]
                                        change = True
                                        for z in range(0,k+1):
                                            if nameFile[0] == str(z):
                                                change = False
                                        if change:
                                            newNameFile = str(k) + '_' + nameFile
                                            adress = str(f).replace(nameFile, newNameFile)
                                            os.rename(str(f), adress)
                                k+=1

                        except  Exception as inst2:
                            if (str(inst2) == "WHEN A CURLY OPENS IT NEEDS TO BE CLOSED! : Didn't find the same number of open curlies then closing curlies"):
                                print('\x1b[1;37;45m' + f"Not the same number of open and closing curlies in Workflow : I don't know how to analyze the workflow yet"+ '\x1b[0m')
                                curly+=1
                                curlies_tab.append(tabWf[i])
                            #Error with a process
                            elif (str(inst2)[:28] == "Couldn't analyze the process"):
                                print('\x1b[1;37;46m' +str(inst)+ '\x1b[0m')
                                problem_process+=1
                                process_tab.append(tabWf[i])
                            #Unknown Error 
                            else:
                                print('\x1b[1;37;41m' + f"Couldn't analyse Workflow : {str(inst)}"+ '\x1b[0m')
                                DSL1_not_analyzed+=1
                                errors.append([tabWf[i], str(inst)])"""
                            
                            
                    #Error not the same number of curlies
                    elif (str(inst) == "WHEN A CURLY OPENS IT NEEDS TO BE CLOSED! : Didn't find the same number of open curlies then closing curlies"):
                        print('\x1b[1;37;45m' + f"Not the same number of open and closing curlies in Workflow : I don't know how to analyze the workflow yet"+ '\x1b[0m')
                        curly+=1
                        curlies_tab.append(tabWf[i])
                    #Error with a process
                    elif (str(inst)[:28] == "Couldn't analyze the process"):
                        print('\x1b[1;37;46m' +str(inst)+ '\x1b[0m')
                        problem_process+=1
                        process_tab.append(tabWf[i])
                    #Unknown Error 
                    else:
                        print('\x1b[1;37;41m' + f"Couldn't analyse Workflow : {str(inst)}"+ '\x1b[0m')
                        DSL1_not_analyzed+=1
                        errors.append([tabWf[i], str(inst)])
                print('')
            #Setting current directory to the root of the results
            res=args.results_directory+'/'+args.name
            os.chdir(res)

            #Saving the results
            s = f'{total} Total\n'
            s+= f'{DSL1_analyzed} DSL1_analyzed\n'
            s+= f'{DSL1_not_analyzed} DSL1_not_analyzed\n'
            s+= f'{DSL2} DSL2\n'
            s+= f'{curly} Curlies\n'
            s+= f'{problem_process} Processes_not_analyzed'
            myText = open('summary'+'.txt','w')
            myText.write(s)
            myText.close()
            print(s )

            myText = open('errors'+'.txt','w')
            for e in errors:
                myText.write(f"file : {e[0]}\nerror : {e[1]}\n\n")
            myText.close()

            myText = open('DSL2_files'+'.txt','w')
            for e in DSL2_tab:
                myText.write(f"{e}\n")
            myText.close()

            myText = open('curlies_files'+'.txt','w')
            for e in curlies_tab:
                myText.write(f"{e}\n")
            myText.close()

            myText = open('analyzed_files'+'.txt','w')
            for e in analyzed_tab:
                myText.write(f"{e}\n")
            myText.close()

            myText = open('process_not_analyzed_files'+'.txt','w')
            for e in process_tab:
                myText.write(f"{e}\n")
            myText.close()

            """#Retrieving the addresses of the nextflow files found at the root of the file
            all_header_files = glob2.glob(args.input+'/**/*.nf')
            print(f'Found {len(all_header_files)} workflows to analyse in {args.input}')
            #Extract the names of the workflows
            names=[]
            for h in all_header_files:
                names.append( h[len(args.input+'/') :(-len('.nf'))])
            #For each workflow
            for i in range(len(names)):
                total+=1
                print(f'{i+1}/{len(all_header_files)}')
                print(f'Analyzing the workflow : {names[i]}')
                #Creating the new folder to save the data from the analyze
                res=args.results_directory+'/'+args.name+'/'+names[i]
                os.system(f"mkdir -p {res}")
                os.chdir(res)
                #Analysing the workflow
                try:
                    w = Workflow(all_header_files[i])
                    w.initialise()
                    DSL1_analyzed+=1
                    analyzed_tab.append(names[i])
                    #Delete developper files if in dev mode
                    if(args.dev != 'F'):
                        os.system('rm channels_extracted.nf')
                        os.system('rm processes_extracted.nf')
                except Exception as inst:
                    #Error DSL2
                    if (str(inst) == "Workflow written in DSL2 : I don't know how to analyze the workflow yet"):
                        print('\x1b[1;37;44m' + f"Workflow written in DSL2 : I don't know how to analyze the workflow yet"+ '\x1b[0m')
                        DSL2+=1
                        DSL2_tab.append(names[i])
                    #Error not the same number of curlies
                    elif (str(inst) == "WHEN A CURLY OPENS IT NEEDS TO BE CLOSED! : Didn't find the same number of open curlies then closing curlies"):
                        print('\x1b[1;37;45m' + f"Not the same number of open and closing curlies in Workflow : I don't know how to analyze the workflow yet"+ '\x1b[0m')
                        curly+=1
                        curlies_tab.append(names[i])
                    #Error with a process
                    elif (str(inst)[:28] == "Couldn't analyze the process"):
                        print('\x1b[1;37;46m' +str(inst)+ '\x1b[0m')
                        problem_process+=1
                        process_tab.append(names[i])
                    #Unknown Error 
                    else:
                        print('\x1b[1;37;41m' + f"Couldn't analyse Workflow : {str(inst)}"+ '\x1b[0m')
                        DSL1_not_analyzed+=1
                        errors.append([names[i], str(inst)])
                print('')
            #Setting current directory to the root of the results
            res=args.results_directory+'/'+args.name
            os.chdir(res)

            #Saving the results
            s = f'{total} Total\n'
            s+= f'{DSL1_analyzed} DSL1_analyzed\n'
            s+= f'{DSL1_not_analyzed} DSL1_not_analyzed\n'
            s+= f'{DSL2} DSL2\n'
            s+= f'{curly} Curlies\n'
            s+= f'{problem_process} Processes_not_analyzed'
            myText = open('summary'+'.txt','w')
            myText.write(s)
            myText.close()
            print(s )

            myText = open('erros'+'.txt','w')
            for e in errors:
                myText.write(f"file : {e[0]}\nerror : {e[1]}\n\n")
            myText.close()

            myText = open('DSL2_files'+'.txt','w')
            for e in DSL2_tab:
                myText.write(f"{e}\n")
            myText.close()

            myText = open('curlies_files'+'.txt','w')
            for e in curlies_tab:
                myText.write(f"{e}\n")
            myText.close()

            myText = open('analyzed_files'+'.txt','w')
            for e in analyzed_tab:
                myText.write(f"{e}\n")
            myText.close()

            myText = open('process_not_analyzed_files'+'.txt','w')
            for e in process_tab:
                myText.write(f"{e}\n")
            myText.close()
"""

    #=========
    # ERROR
    #=========
    else:
        raise Exception(f"Neither single or multiple workflow analysis was selected, but '{args.mode}'")
    
    #When finished setting directory to the original directory
    os.chdir(current_directory)
