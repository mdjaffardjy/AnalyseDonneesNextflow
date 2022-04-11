# Nextflow Analyzer
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022

import re
from pathlib import Path

from .process import *
from .file import *
from .typeMain import *
from .typeMainDSL1 import *
from .typeMainDSL2 import *


class Workflow:
    def __init__(self, address):
        #Bool if the workflow is using the syntax extension or not
        self.is_DSL2 = None
        #Address of the main
        self.address_main = address
        #The main of the Workflow
        self.main = None


    #Checks if the workflow is using DSL2
    def check_DSL2(self):
        #Pattern found in the source code of nextflow
        pattern= r'(nextflow\.(preview|enable)\.dsl\s*=\s*2)'
        #Checks if the pattern is found in the main 
        #So we create a temporary File type
        temp= File(self.address_main)
        temp.initialise_basic_file()
        code= temp.get_string()
        self.is_DSL2 = bool(re.compile(pattern).search(code))

    #Returns the bool corresponding to DSL2?
    def get_DSL2(self):
        return self.is_DSL2
    
    #Initialises the main
    def initialise_main(self):
        #Case DSL=1
        if(not self.get_DSL2()):
            print('Workflow written in DSL1')
            self.main= TypeMainDSL1(self.address_main)
            self.main.initialise()

        #Case DSL=2
        elif(self.get_DSL2()):
            raise Exception("Single file is written in DSL2 : I don't know how to analyze this yet")

    
    #Initialise the workflow
    def initialise(self):
        #Checking that it's a file -> supposed a workflow written in DSL1 in this case
        if Path(self.address_main).is_file():
            #Check to see if the workflow is written is DSL2 or not
            self.check_DSL2()
            #Analyze the workflow
            self.initialise_main()
        #If it's a folder it's supposed that it is a workflow written in DSL2 
        else:
            self.main= TypeMainDSL2(self.address_main)
            self.main.initialise()




