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


def is_directory(adress):
    for i in range(-1,-1-len(adress), -1):
        if(adress[i]=='.'):
            return False
        elif(adress[i]=='/'):
            return True

#Color follows the pattern 'int; int; int'
def print_in_color(text, color):
    print('\x1b['+color+'m' + text + '\x1b[0m')


def main():
    current_directory = os.getcwd()
    
    parser = argparse.ArgumentParser()
    #Obligatory
    parser.add_argument('input') 
    parser.add_argument('results_directory')
    #Facultatif
    parser.add_argument('--name', default='Workflow_Analysis')
    parser.add_argument('--mode', default='single')

    args = parser.parse_args() 
    
    #Changing to the directory where the extracted data will be saved
    os.chdir(args.results_directory)

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
            #Creating the new directory if it doesn't exist
            os.system(f"mkdir -p {args.name}")
            #Moving to the new directory
            res=args.results_directory+'/'+args.name
            os.chdir(res)
            
            #Analysing the workflow
            w = Workflow(args.input)
            w.initialise()
            
            print(f'Results saved in : {res}')
        else:
            raise Exception('\x1b[1;37;41m' + f"Either '{args.input}' is not a file or doesn't exist!!"+ '\x1b[0m')
    
    #=========
    # MULTI
    #=========
    elif(args.mode == 'multi'):
        total, DSL2, DSL1_analyzed, DSL1_not_analyzed, curly= 0, 0, 0, 0, 0
        errors, DSL2_tab, curlies_tab, analyzed_tab = [], [], [], []
        print('')
        print('\x1b[7;33;40m' + 'Multiple Workflow analysis mode was selected' + '\x1b[0m')
        print('')
        #Checking that input is not a file
        if Path(args.input).is_file():
            raise Exception('\x1b[1;37;41m' + f"'{args.input}' is file, a directory is expected for multi mode!!"+ '\x1b[0m')
        else:
            all_header_files = glob2.glob(args.input+'/*.nf')
            print(f'Found {len(all_header_files)} workflows to analyse in {args.input}')
            names=[]
            for h in all_header_files:
                names.append( h[len(args.input+'/') :(-len('.nf'))])
            
            for i in range(len(names)):
                total+=1
                print(f'{i+1}/{len(all_header_files)}')
                print(f'Analyzing the workflow : {names[i]}')
                res=args.results_directory+'/'+args.name+'/'+names[i]
                os.system(f"mkdir -p {res}")
                os.chdir(res)
                #Analysing the workflow
                try:
                    w = Workflow(all_header_files[i])
                    w.initialise()
                    DSL1_analyzed+=1
                    analyzed_tab.append(names[i])
                except Exception as inst:
                    if (str(inst) == "Workflow written in DSL2 : I don't know how to analyze the workflow yet"):
                        print('\x1b[1;37;44m' + f"Workflow written in DSL2 : I don't know how to analyze the workflow yet"+ '\x1b[0m')
                        DSL2+=1
                        DSL2_tab.append(names[i])
                    elif (str(inst) == "WHEN A CURLY OPENS IT NEEDS TO BE CLOSED! : Didn't find the same number of open curlies then closing curlies"):
                        print('\x1b[1;37;45m' + f"Not the same number of open and closing curlies in Workflow : I don't know how to analyze the workflow yet"+ '\x1b[0m')
                        curly+=1
                        curlies_tab.append(names[i])
                    
                    else:
                        print('\x1b[1;37;41m' + f"Couldn't analyse Workflow : {str(inst)}"+ '\x1b[0m')
                        DSL1_not_analyzed+=1
                        errors.append([names[i], str(inst)])
                print('')
            res=args.results_directory+'/'+args.name
            os.chdir(res)

            s = f'{total} Total\n'
            s+= f'{DSL1_analyzed} DSL1_analyzed\n'
            s+= f'{DSL1_not_analyzed} DSL1_not_analyzed\n'
            s+= f'{DSL2} DSL2\n'
            s+= f'{curly} Curlies'
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


    #=========
    # ERROR
    #=========
    else:
        raise Exception(f"Neither single or multiple workflow analysis was selected, but '{args.mode}'")
    
    #At the end : return to the original directory
    os.chdir(current_directory)



#IMPORTANT!!!
#lOOK AT the config file for the names of the workflow and the link to the main
if __name__ == "__main__":
    from workflow import *
    #Right now we're supposing that the address which is given is the "root" of the workflow project
    #The main.nf is situadted at the root
    #In the case of DSL2 all the nextflow files in that root (recursevely) will be analysed and the structure reconstructed
    """address= input("What's the adress of the workflow? ==> ")
    print("\n")
    
    w1= Workflow(address)
    w1.initialise()
    """
    adress= '/home/george/Bureau/TER/processes.nf'

    print(is_directory(adress))

    if(not is_directory(adress)):
        if Path(adress).is_file():
            print ("File exist")
        else:
            print ("File not exist")