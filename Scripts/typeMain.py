from .file import *

class TypeMain(File):
    def __init__(self, address):
        super().__init__(address)
        

    #Initialise the basic stuff for a mains type
    def initialise_basic_main(self):
        self.initialise_basic_file()


