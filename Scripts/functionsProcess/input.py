from functionsProcess.commonFunction import *
import re
"""
FIRST PART
""" 

keyWordsI = ['val', 'env', 'file', 'path', 'stdin', 'tuple', 'each', 'set']

listPatternI = []
for words in keyWordsI:
    string = "([^,]\\n+\\s*" + words + "[^a-zA-Z0-9])"
    listPatternI.append(string)

listPatternIb = []
for words in keyWordsI:
    string = "(" + words + "(\s|\(|\{|\[)\w+)"
    listPatternIb.append(string)

"""
SECOND PART - Class
"""
class Inputs:
    def __init__(self, strInput):
        self.input_string = strInput
        self.list_input = []
        self.list_qualifier = []
        self.list_words_workflow = []

    def printInput(self):
        print(self.input_string)

    def printListInput(self):
        for string in self.list_input:
            print(string)

    def numberInputs(self):
        return len(self.list_input)
    
    def getQualifier(self):
        return self.list_qualifier
    
    def getInputs(self):
        return self.list_input
    
    def getNameInWorkflow(self):
        return self.list_words_workflow
        
    def splitInput(self):
        self.list_input = split(listPatternI, self.input_string)

    def extractQualifier(self):
        self.list_qualifier = extractQ(self.list_input)

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
                string = self.list_input[idx][start:end].lstrip().rstrip()
                self.list_words_workflow.append([idx,string])
            #Without "from"
            else:
                startb = -1
                for i in range(len(listPatternIb)):
                    pat = listPatternIb[i]
                    for match in re.finditer(pat,self.list_input[idx]):
                        startb = match.span()[0] + len(keyWordsI[i]) + 1
                        endb = match.span()[1]
                    if startb >=0:
                        string = self.list_input[idx][startb:endb].lstrip().rstrip()
                        if string[0].isalpha():
                            self.list_words_workflow.append([idx,string])
                        else:
                            self.list_words_workflow.append([idx,string[1:]])
                        break
                    
    def extractI(self):
        self.splitInput()
        self.extractQualifier()
        self.extractName() #For Parser : name in the process

    
if __name__ == "__main__":
    print("I shouldn't be executed as a main")
