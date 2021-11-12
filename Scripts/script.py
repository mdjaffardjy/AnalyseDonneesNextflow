from process import *

import re

class Script:
    def __init__(self, strScript):
            self.script_string = strScript
            self.language = []

    def printString(self):
        print(self.script_string)  
    
    def printLanguage(self):
        str = ""
        for i in range (len(self.language)):
            if i != len(self.language)-1:
                str +=self.language[i] + " - "
            else:
                str += self.language[i]
        return str

    def getLanguage(self):
        return self.language
    
    def whichLanguage(self):
        pattern = r'(#!\/usr\/bin\/)'
        start = len(self.script_string)
        nb = -1
        for match in re.finditer(pattern, self.script_string):
            start = match.span()[1]
            nb = 1
        if nb < 0:
            self.language.append('bash')
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
            self.language.append(language)




    def extractS(self):
        self.whichLanguage()


##!/usr/bin/

        
if __name__ == "__main__":
    print("I shouldn't be executed as a main")
