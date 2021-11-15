from process import *

import re
"""
FIRST PART
""" 

keyWordsI = ['val', 'env', 'file', 'path', 'stdin', 'tuple', 'each', 'set']

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
        self.list_words_workflow = []

    def printInput(self):
        print(self.input_string)

    def printListInput(self):
        for str in self.list_input:
            print(str)

    def numberInputs(self):
        return len(self.list_input)
    
    def getQualifier(self):
        return self.qualifier
    
    def getInputs(self):
        return self.list_input
    
    def getNameInWorkflow(self):
        return self.list_words_workflow
        
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

    def extractName(self):
        """pattern = r'(\sfrom\s*\w*)'
        for l in self.list_input:
            start = -1
            for match in re.finditer(pattern, l):
                start = match.span()[0] + len("from")+1
                end = match.span()[1]
            if start >= 0:
                str = l[start:end].lstrip().rstrip()
                self.list_words_workflow.append(str)"""

        pattern = r'(\sfrom\s*((\'|")+.*(\'|")*|\w*))'
        for l in self.list_input:
            start = -1
            for match in re.finditer(pattern, l):
                start = match.span()[0] + len("from")+1
                end = match.span()[1]
            if start >= 0:
                str = l[start:end].lstrip().rstrip()
                self.list_words_workflow.append(str)
              

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
        self.extractName() #For Parser : name in the process

    
if __name__ == "__main__":
    print("I shouldn't be executed as a main")
