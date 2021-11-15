from process import *

import re
"""
FIRST PART
""" 
keyWordsO = ['val', 'env', 'file', 'path', 'stdout', 'tuple', 'set']

listPatternO = []
for words in keyWordsO:
    str = "([^,]\\n+\\s*" + words + "[^a-zA-Z0-9])"
    listPatternO.append(str)

"""
SECOND PART - Class
"""
class Outputs:
    def __init__(self, strOutput):
        self.output_string = strOutput
        self.list_output = []
        self.qualifier = {}
        self.list_words_workflow = []

    def printOutput(self):
        print(self.output_string)

    def printListOutput(self):
        for str in self.list_output:
            print(str)

    def numberOutputs(self):
        return len(self.list_output)

    def getQualifier(self):
        return self.qualifier
    
    def getOutputs(self):
        return self.list_output
    
    def getNameInWorkflow(self):
        return self.list_words_workflow
        
    def splitOutput(self):
        work = "a \n" + self.output_string #for the first one
        index = []
        for pattern in listPatternO:
            for match in re.finditer(pattern, work):
                index.append(match.span()[0]+1)
        index.sort()
        for i in range (len(index)):
            if i == len(index)-1:
                output = work[index[i]:].lstrip().rstrip()
            else:   
                output = work[index[i]:index[i+1]].lstrip().rstrip()
            self.list_output.append(output)
    
    def extractName(self):
        pattern = r'(\sinto\s*((\'|")+.*(\'|")*|\w*))'
        for l in self.list_output:
            start = -1
            for match in re.finditer(pattern, l):
                start = match.span()[0] + len("into")+1
                end = match.span()[1]
            if start >= 0:
                str = l[start:end].lstrip().rstrip()
                self.list_words_workflow.append(str)

    def analyseQualifier(self):
        for str in self.list_output:
            cut = re.split("[^\w]", str)
            key = cut[0]
            if key in self.qualifier:
                self.qualifier[key] += 1
            else:
                self.qualifier.update({key:1})

    def extractO(self):
        self.splitOutput()
        self.analyseQualifier()
        self.extractName()

    
if __name__ == "__main__":
    print("I shouldn't be executed as a main")
