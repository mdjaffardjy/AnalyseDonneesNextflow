import re
from typeMain import * 
from process_test import *

class TypeMainDSL1(TypeMain):
    def __init__(self, address):
        super().__init__(address)
        self.processes=[]


    def extract_processe(self, start):
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

    def find_processes(self):
        pattern= r'(process\s*\w*\s*{)'
        for match in re.finditer(pattern, self.string):
            #print(self.string[match.span()[0]:match.span()[1]])
            start= match.span()[0]
            end= self.extract_processe(match.span()[1])
            process= Process(self.string[start:end])
            process.extractProcess()
            self.processes.append(process)
    
    def print_name_processes(self):
        for p in self.processes:
            p.printName()

    def initialise(self):
        self.initialise_basic_main()
        self.find_processes()
        None

if __name__ == "__main__":
    #print("I shoudn't be executed as a main")
    m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/eager-master/main.nf")
    m.initialise()
    m.print_name_processes()