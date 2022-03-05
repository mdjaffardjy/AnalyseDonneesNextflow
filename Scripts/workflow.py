import re
import glob
import os

from .process import *
from .file import *
from .typeMain import *
from .typeMainDSL1 import *
from .typeMainDSL2 import *


class Workflow:
    def __init__(self, address):
        #Name of the Project
        self.name = None
        #Bool if the workflow is using the syntax extension or not
        self.is_DSL2 = None
        #Address of the main
        self.address_main = address
        #The main of the Project
        self.main = None


    
    #Get the last word the path
    #Sets the name of the project
    def set_name(self):
        indice=-1
        if(self.root[indice]=='/'):
            indice -= 1
        start= indice+len(self.root)+1
        while(self.root[indice]!='/'):
            indice-=1
        end= indice+len(self.root)+1
        #print(start, end)
        self.name = self.root[end:start]
        

    #Returns the name of the project
    def get_name(self):
        return self.name

    
    #Sets the address of the main
    #We assume that the main is set at the root
    def set_address_main(self):
        elements_in_directory= os.listdir(self.root)
        if(not 'main.nf' in elements_in_directory):
            raise Exception("No 'main.nf' found in directory!")
        self.address_main = self.root + '/main.nf'
           

    #Returns address of main
    def get_address_main(self):
        return self.address_main

    #Checks if the workflow is using DSL2
    def check_DSL2(self):
        #Pattern found in the source code of nextflow
        pattern= r'(nextflow\.(preview|enable)\.dsl\s*=\s*2)'
        #Checks if the pattern is found in the main file
        #So we create a temporary main type
        temp_main= TypeMain(self.address_main)
        temp_main.initialise_basic_main()
        code= temp_main.get_string()
        self.is_DSL2 = bool(re.compile(pattern).search(code))

    #Returns the bool corresponding to DSL2?
    def get_DSL2(self):
        return self.is_DSL2
    
    #Initialises the main => creates the right DSL type
    def initialise_main(self):
        #Case DSL=1
        if(not self.get_DSL2()):
            print('Workflow written in DSL1')
            self.main= TypeMainDSL1(self.address_main)
            self.main.initialise()
            #nb_process, nb_links= self.main.get_structure_4(self.name, self.address_to_save_files)
            #return nb_process, nb_links
            #self.main.save_file()
            #self.main.save_channels()
            #self.main.save_processes()
        #Case DSL=2
        elif(self.get_DSL2()):
            raise Exception("Workflow written in DSL2 : I don't know how to analyze the workflow yet")
            #print('\x1b[1;37;41m' + f"Workflow written in DSL2 : I don't know how to analyze the workflow yet"+ '\x1b[0m')
            """self.main= TypeMainDSL2(self.address_main)
            self.main.initialise()
            return -1"""
        

    
    #Initialise the workflow
    def initialise(self):
        #self.set_name()
        #self.set_address_main()
        self.check_DSL2()
        self.initialise_main()
        #print(self.main)

#=================
#IF USED AS A MAIN
#=================
if __name__ == "__main__":
    #print("I shoudn't be executed as a main")
    #DSL1
    w= Workflow("/home/george/Bureau/TER/Workflow_Database/samba-master", '/home/george/Bureau/')
    #w= Workflow("/home/george/Bureau/TER/Workflow_Database/eager-master")
    #DSL2
    #w= Workflow("/home/george/Bureau/TER/Workflow_Database/rnaseq-master")
    a, b= w.initialise()
    print(a,b)
    print(w.get_DSL2())

def test_func(name, root, dirc):
    w= Workflow(root, dirc)
    #w.initialise()
    w.name = name
    w.address_main= root
    nb_process, nb_links = w.initialise_main()
    return nb_process, nb_links
    
#TODO list 


