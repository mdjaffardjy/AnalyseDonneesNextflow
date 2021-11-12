from process import *

import re
"""
FIRST PART
""" 

keyWordsI = ['val', 'env', 'file', 'path', 'stdin', 'tuple', 'each', 'set']

# [^,]\n+\s*set[^a-zA-Z0-9]
listPatternI = []
for words in keyWordsI:
    str = "([^,]\\n+\\s*" + words + "[^a-zA-Z0-9])"
    listPatternI.append(str)

"""
SECOND PART - Class
"""
class Inputs:
    def __init__(self, strInput):
        self.input_string = strInput
        self.list_input = []
        self.qualifier = {}

    def printInput(self):
        print(self.input_string)

    def printListInput(self):
        for str in self.list_input:
            print(str)

    def numberInputs(self):
        return len(self.list_input)

    def printQualifier(self):
        print(self.qualifier)
    
    def getQualifier(self):
        return self.qualifier
        
    def splitInput(self):
        work = "a \n" + self.input_string
        index = []
        for pattern in listPatternI:
            for match in re.finditer(pattern, work):
                index.append(match.span()[0]+1)
        index.sort()
        for i in range (len(index)):
            if i == len(index)-1:
                input = work[index[i]:].lstrip().rstrip()
            else:   
                input = work[index[i]:index[i+1]].lstrip().rstrip()
            self.list_input.append(input)


    def analyseQualifier(self):
        for str in self.list_input:
            cut = re.split("[^\w]", str)
            key = cut[0]
            if key in self.qualifier:
                self.qualifier[key] += 1
            else:
                self.qualifier.update({key:1})

    def extractI(self):
        self.splitInput()
        self.analyseQualifier()

    
if __name__ == "__main__":
    print("I shouldn't be executed as a main")
