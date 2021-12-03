from functionsProcess.commonFunction import * 
from functionsProcess.toolFunction import *

class Stub:
    def __init__(self, strStub):
            self.stub_string = strStub
            self.language = None
            self.tools = None
            self.annotations = None

    def printString(self):
        print(self.stub_string)  
    
    def printLanguage(self):
        print(self.language)

    def getLanguage(self):
        return self.language
    
    def getTools(self):
        return self.tools
    
    def getAnnotations(self):
        return self.annotations

    def whichLanguage(self):
        self.language = whichLanguage(self.stub_string)

    def extractTools(self):
        work = justScript(self.stub_string)
        self.tools = get_toolnames(work)
        self.annotations = get_info_biotools_set_of_tools_dump(self.tools)

    def extractS(self):
        self.whichLanguage()
        self.extractTools()
        
if __name__ == "__main__":
    print("I shouldn't be executed as a main")

