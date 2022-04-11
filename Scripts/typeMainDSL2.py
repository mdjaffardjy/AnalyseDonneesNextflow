# Nextflow Analyzer
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022

import glob2

from .typeMain import * 
from .process import *


class TypeMainDSL2(TypeMain):
    def __init__(self, address):
        super().__init__(address)
        
    
    def initialise(self):
        print("Workflow written in DSL2")
        #Get all nextflow files in address
        all_header_files = glob2.glob(self.address+'/**/*.nf')
        print(f'Found {len(all_header_files)} nextflow files to analyse in {self.address}')
        #For each file found
        for f in all_header_files:
            next_file = TypeMain(f)
            #Initialize
            next_file.initialise_basic_main()
            #Find and analyze the processes
            next_file.find_processes()
            #Retrieve the processes
            pro = next_file.get_processes()
            print(f'Analyzing {f[len(self.address):]} : {len(pro)} processes found')
            #Add the processes to the list of processes
            self.processes += pro
        print(f'Total number of processes in the workflow {self.get_name_workflow()} : {len(self.processes)}')
        #Save the processes
        self.get_info_processes()

