# Nextflow Analyzer
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022

import re
import os
from select import select
import graphviz
import json
import glob2

from .typeMain import * 
from .process import *


class TypeMainDSL2(TypeMain):
    def __init__(self, address):
        super().__init__(address)
        
        

    #Initialise the basic stuff for a mainDSL2 type
    def initialise(self):
        print("Workflow written in DSL2")
        all_header_files = glob2.glob(self.address+'/**/*.nf')
        #print(all_header_files)
        print(f'Found {len(all_header_files)} nextflow files to analyse in {self.address}')
        for f in all_header_files:
            
            next_file = TypeMain(f)
            next_file.initialise_basic_main()
            next_file.find_processes()
            pro = next_file.get_processes()
            print(f'Analyzing {f[len(self.address):]} : {len(pro)} processes found')
            self.processes += pro
        
        print(f'Total number of processes in the workflow {self.get_name_workflow()} : {len(self.processes)}')
        self.get_info_processes()

