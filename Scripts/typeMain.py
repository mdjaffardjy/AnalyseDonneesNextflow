# Nextflow Analyzer
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022

import json

from .file import *
from .process import *

class TypeMain(File):
    def __init__(self, address):
        super().__init__(address)
        self.processes=[]
        self.analyze_processes = True
        

    #===========================================
    #UTILITY METHODS
    #===========================================
    #Intermediate method that 'finds' the end of the process or functions, when we give the start position
    #So it follows the pattern 'process name {....}' or def name(..){...}
    def extract_curly(self, start):
        count_curly = 1
        end = start
        work= self.string
        while(count_curly != 0):
            #print(work[end])
            if(work[end] == "{"):
                count_curly += 1
            elif(work[end] == "}"):
                count_curly -= 1
            end += 1
        return end

    def right_nb_curly(self):
        if(self.string.count('{')==self.string.count('}')):
            return True
        return False

    def get_name_workflow(self):
        t = os.getcwd()
        i=-1
        while(t[i] != '/'):
            i-=1
        self.name_workflow = t[(i+1):len(t)]
        return self.name_workflow




    #===========================================
    #METHODS FOR MANIPULATING PROCESSES
    #===========================================
    #Finds and adds the processes to the list of processes + analyses them
    def find_processes(self):
        pattern=  r'([^\w]?process\s+\w+\s*{)'
        for match in re.finditer(pattern, self.string):
            start= match.span()[0]
            end= self.extract_curly(match.span()[1])
            process= Process(self.string[start:end])
            process.extractProcess(analyse_tools=self.analyze_processes)
            self.processes.append(process)   
    
    #Print the names of the different processes
    def print_name_processes(self):
        for p in self.processes:
            p.printName()

    #Return the number of processes
    def get_nb_processes(self):
        return len(self.processes)

    #Print the different processes
    def print_processes(self):
        for i in range(len(self.processes)):
            print(self.processes[i].get_string())

    #Removes the processes from the workflow string (this simplifies the analysis)
    def format_processes(self):
        for p1 in self.processes:
            i=-1
            for p2 in self.processes:
                if(p1.get_name()==p2.get_name()):
                    i+=1
            if(i>0):
                p1.change_name(p1.get_name()+'_'+str(i))
        for i in range(len(self.processes)):
            self.string= self.string.replace(self.processes[i].get_string(), 'PROCESS DEF '+self.processes[i].get_name(), 1)
    
    def save_processes(self, name='processes_extracted'):
        myText = open(name+'.nf','w')
        for p in self.processes:
            #myText.write(str(c.get_gives())+' <- '+c.get_string()+'\n\n')
            myText.write('Name : '+p.getName()+'\n')
            input, output, emit= p.extractAll()
            myText.write('Inputs : '+  str(input)+'\n')
            myText.write('Outputs : '+  str(output)+'\n')
            myText.write('Emits : '+  str(emit)+'\n\n\n')
        myText.close()
    
    #Return the processes found
    def get_processes(self):
        return self.processes

    
    def get_info_processes(self, name='processes_info'):
        if(self.analyze_processes):
            dict={}
            #For each process we get it's corresponding data
            for p in self.processes:
                dict[p.getName()] = {}
                dict[p.getName()]['name_process']= p.getName()
                def get_number_lignes(string):
                    nb=0
                    for s in string:
                        if(s=='\n'):
                            nb+=1
                    return nb 
                dict[p.getName()]['string_process']= p.get_string()
                #We remove one since we do not want the definition ligne to count : not really really important
                dict[p.getName()]['nb_lignes_process']= get_number_lignes(p.get_string())-1
                dict[p.getName()]['string_script']= p.get_string_script()
                #In this case we leave the ligne corresponding to """ since they all have it => it doesn't matter
                dict[p.getName()]['nb_lignes_script']= get_number_lignes(p.get_string_script())
                dict[p.getName()]['language_script']= p.getScriptLanguage()
                dict[p.getName()]['tools']= p.getListTools()
                inputs, outputs, emits=p.extractAll()
                def simplify(tab):
                    temp=[]
                    for t in tab:
                        temp.append(t[1])
                    return temp
                dict[p.getName()]['inputs']= simplify(inputs)
                dict[p.getName()]['nb_inputs']= len(inputs)
                dict[p.getName()]['outputs']= simplify(outputs)
                dict[p.getName()]['nb_outputs']= len(outputs)

                dict[p.getName()]['name_workflow']= self.get_name_workflow()
                
                
                dict[p.getName()]['directive']= p.getDirectiveList()
                dict[p.getName()]['when']= p.getWhen()
                dict[p.getName()]['stub']= p.getStub()
            with open(name+'.json', "w") as outfile:
                json.dump(dict, outfile, indent=4)
        

    #Initialise the basic stuff for a mains type
    def initialise_basic_main(self):
        self.initialise_basic_file()


