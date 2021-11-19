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

listPatternIb = []
for words in keyWordsI:
    str = "(" + words + "(\s|\(|\{|\[)\w+)"
    listPatternIb.append(str)

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

            antiSlash = []
            for match in re.finditer(r"(\\)", input):
                    antiSlash.append(match.span())
            antiSlash.sort(reverse = True)
            for j in range(len(antiSlash)):
                input = input.replace(input[antiSlash[j][0]:antiSlash[j][1]], " ")
            input =" ".join(input.split())
            self.list_input.append(input)

    def extractName(self):
        #Two Cases : 
        pattern = r'(\sfrom\s\w+)'
        for idx in range (len(self.list_input)):
            start = -1 
            for match in re.finditer(pattern, self.list_input[idx]):
                start = match.span()[0] + len("from") +1
                end = match.span()[1]
            #Precence of "from"
            if start >=0:
                str = self.list_input[idx][start:end].lstrip().rstrip()
                self.list_words_workflow.append([idx,str])
            #Without "from"
            else:
                startb = -1
                for i in range(len(listPatternIb)):
                    pat = listPatternIb[i]
                    for match in re.finditer(pat,self.list_input[idx]):
                        startb = match.span()[0] + len(keyWordsI[i]) + 1
                        endb = match.span()[1]
                    if startb >=0:
                        str = self.list_input[idx][startb:endb].lstrip().rstrip()
                        if str[0].isalpha():
                            self.list_words_workflow.append([idx,str])
                        else:
                            self.list_words_workflow.append([idx,str[1:]])
                        break

              

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
