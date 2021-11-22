from process import *
from commonFunction import * 

class Stub:
    def __init__(self, strStub):
            self.stub_string = strStub
            self.language = None

    def printString(self):
        print(self.stub_string)  
    
    def printLanguage(self):
        print(self.language)

    def getLanguage(self):
        return self.language
    
    def whichLanguage(self):
        self.language = whichLanguage(self.stub_string)

    def extractS(self):
        self.whichLanguage()
        
if __name__ == "__main__":
    print("I shouldn't be executed as a main")

