import re
import glob

#from process import *
from file import *
from typeMain import *
from typeMainDSL1 import *
from typeMainDSL2 import *


class Workflow:
    def __init__(self, root):
        #Name of the Project
        self.name = None
        #Root address
        self.root = root
        #Bool if the workflow is using the syntax extension or not
        self.is_DSL2 = None
        #Address of the main
        self.address_main = None
        #The main of the Project
        self.main = None

    #TODO
    #Get the last word the path
    #Sets the name of the project
    def set_name(self):
        self.name= 'Temporary_Name'

    #Returns the name of the project
    def get_name(self):
        return self.name

    #TODO
    #Sets the address of the main
    #We assume that the main is set at the root
    def set_address_main(self):
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
            self.main= TypeMainDSL1(self.address_main)
        #Case DSL=2
        elif(self.get_DSL2()):
            self.main= TypeMainDSL2(self.address_main)
        self.main.initialise()

    
  
    #TODO
    #Initialise the workflow
    def initialise(self):
        self.set_name()
        self.set_address_main()
        self.check_DSL2()
        self.initialise_main()
        print(self.main)


if __name__ == "__main__":
    #print("I shoudn't be executed as a main")
    w= Workflow("/home/george/Bureau/TER/Workflow_Database/samba-master")
    w.initialise()
    print(w.get_DSL2())
    
#TODO list 
#   - Finish the rest of the TODOs
