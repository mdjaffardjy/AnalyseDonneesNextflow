import re
from typeMain import * 
from process_test import *

class TypeMainDSL1(TypeMain):
    def __init__(self, address):
        super().__init__(address)
        self.processes=[]

    #Intermediate method that 'finds' the end of the process, when we give the start position
    #So it follows the pattern 'process name {....}'
    def extract_process(self, start):
        count_curly = 1
        end = start
        work= self.string
        while(count_curly != 0):
            if(work[end] == "{"):
                count_curly += 1
            elif(work[end] == "}"):
                count_curly -= 1
            end += 1
        return end

    #Finds and adds the processes to the list of processes
    def find_processes(self):
        pattern= r'(process\s*\w*\s*{)'
        for match in re.finditer(pattern, self.string):
            #print(self.string[match.span()[0]:match.span()[1]])
            start= match.span()[0]
            end= self.extract_process(match.span()[1])
            process= Process(self.string[start:end])
            process.extractProcess()
            self.processes.append(process)
    
    #Print the names of the different processes
    def print_name_processes(self):
        for p in self.processes:
            p.printName()

    #Return the number of processes
    def get_nb_processes(self):
        return len(self.processes)

    #Finds the channels and adds them to the list of Channels
    def find_channels(self):
        pattern_basic= r'((c|C)hannel[ \n]*\.)'

    #Initialise the basic stuff for a mainDSL1 type
    def initialise(self):
        self.initialise_basic_main()
        self.find_processes()
        None

if __name__ == "__main__":
    #print("I shoudn't be executed as a main")
    m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/eager-master/main.nf")
    m.initialise()
    m.print_name_processes()
    #m.print_file()


#TODO List
#
# - Think about how to deal with channels and functions
# - And to link everything together after
    