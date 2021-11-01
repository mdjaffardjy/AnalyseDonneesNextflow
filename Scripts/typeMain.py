
from file import *

class TypeMain(File):
    def __init__(self, address):
        super().__init__(address)
        


    def initialise_basic_main(self):
        self.initialise_basic_file()

if __name__ == "__main__":
    print("I shoudn't be executed as a main")
    
    """m= TypeMain("/home/george/Bureau/TER/Workflow_Database/samba-master/main.nf")
    m.initialise_basic_main()
    m.print_file()#"""
    

#TODO list:
#   - Extract Processes
#   - Extract Functions
#   - Extract Channels (-> structure)