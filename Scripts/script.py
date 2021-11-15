from process import *

import re

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
    
    #Extract language 
    """
    First : search the pattern which show the language
    If doesn't find : bash 
    Else : we find the end of the line and search the language between the start and the end
    """
    def whichLanguage(self):
        pattern = r'(#!\/usr\/bin\/)'
        start = len(self.script_string)
        nb = -1
        for match in re.finditer(pattern, self.script_string):
            start = match.span()[1]
            nb = 1
        if nb < 0:
            self.language = 'bash'
        else:
            patternEnd = r'(\n)'
            end = len(self.script_string)
            for match in re.finditer(patternEnd, self.script_string):
                if match.span()[0] < end and match.span()[0] > start:
                    end = match.span()[0]
            patEnv = r'(env)'
            language = self.script_string[start:end].lstrip().rstrip()
            for match in re.finditer(patEnv, language):
                language = language[match.span()[1]:].lstrip() 
            self.language = language

    def extractS(self):
        self.whichLanguage()
      
if __name__ == "__main__":
    print("I shouldn't be executed as a main")
