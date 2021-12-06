from functionsProcess.commonFunction import *
from functionsProcess.toolFunction import *

class Script:
    def __init__(self, strScript):
            self.script_string = strScript
            self.language = None
            self.tools = []
            self.annotations = {}

    def printString(self):
        print(self.script_string)  
    
    def printLanguage(self):
        print(self.language)

    def getLanguage(self):
        return self.language
    
    def getTools(self):
        return self.tools
    
    def getAnnotations(self):
        return self.annotations
    
    def whichLanguage(self):
        self.language = whichLanguage(self.script_string)

    def extractTools(self):
        #print("SCRIPT:")
        #print(self.script_string)
        if self.language == 'bash':
            work = justScript(self.script_string)
            #print(work)
            self.tools = get_toolnames(work)
            self.annotations = get_info_biotools_set_of_tools_dump(self.tools)
        #print()

    def extractS(self):
        self.whichLanguage()
        self.extractTools()

if __name__ == "__main__":
    print("I shouldn't be executed as a main")