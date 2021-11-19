from process import *
import re

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
    
    #Extract language 
    """
    First : search the pattern #!/usr/bin/
    If doesn't find : bash 
    Else : we find the end of the line and search the language between the start and the end
    """
    def whichLanguage(self):
        pattern = r'(#!\/usr\/bin\/)'
        start = len(self.stub_string)
        nb = -1
        for match in re.finditer(pattern, self.stub_string):
            start = match.span()[1]
            nb = 1
        if nb < 0:
            self.language = 'bash'
        else:
            patternEnd = r'(\n)'
            end = len(self.stub_string)
            for match in re.finditer(patternEnd, self.stub_string):
                if match.span()[0] < end and match.span()[0] > start:
                    end = match.span()[0]
            patEnv = r'(env)'
            language = self.stub_string[start:end].lstrip().rstrip()
            for match in re.finditer(patEnv, language):
                language = language[match.span()[1]:].lstrip() 
            self.language = language

    def extractS(self):
        self.whichLanguage()
        
if __name__ == "__main__":
    print("I shouldn't be executed as a main")

