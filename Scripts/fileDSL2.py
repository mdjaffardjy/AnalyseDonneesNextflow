from file import *
import re
import graphviz

class FileDSL2(File):
    def __init__(self, address, root):
        super().__init__(address)
        self.root= root
        

    #Initialise the basic stuff for a mains type
    def initialise_basic_main(self):
        self.initialise_basic_file()
