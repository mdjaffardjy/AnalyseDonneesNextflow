from process import *
from commonFunction import *

class Script:
    def __init__(self, strScript):
            self.script_string = strScript
            self.language = None

    def printString(self):
        print(self.script_string)  
    
    def printLanguage(self):
        print(self.language)

    def getLanguage(self):
        return self.language
    
    def whichLanguage(self):
        self.language = whichLanguage(self.script_string)

    def extractS(self):
        self.whichLanguage()
      
if __name__ == "__main__":
    print("I shouldn't be executed as a main")
