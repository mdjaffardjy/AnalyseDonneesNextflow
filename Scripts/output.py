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

listPatternOb = []
for words in keyWordsO:
    str = "(" + words + "(\s|\(|\{|\[)\w+)"
    listPatternOb.append(str)

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

            antiSlash = []
            for match in re.finditer(r"(\\)", output):
                    antiSlash.append(match.span())
            antiSlash.sort(reverse = True)
            for j in range(len(antiSlash)):
                output = output.replace(output[antiSlash[j][0]:antiSlash[j][1]], " ")

            output =" ".join(output.split())            
            self.list_output.append(output)
    
    def extractName(self):
        #Two Cases : 
        pattern = r'(\sinto\s((\w+\s*,?\s*))*)'
        for idx in range(len(self.list_output)):
            start = -1 
            for match in re.finditer(pattern, self.list_output[idx]):
                start = match.span()[0] + len("into") +1
                end = match.span()[1]
                work = self.list_output[idx][start:end].lstrip().rstrip()
            #Precence of "into"
            if start >=0:
                comma = r'(,)'
                placeComma = []
                for match in re.finditer(comma,work):
                    placeComma.append(match.span())
                if len(placeComma) == 0:
                    endWord = r'($|\s)'
                    end = len(work)+1
                    for match in re.finditer(endWord, work):
                        if match.span()[0] < end:
                            end = match.span()[0]
                    str = work[:end].lstrip().rstrip()
                    self.list_words_workflow.append([idx,str])
                else:
                    placeComma.sort()
                    for i in range (len(placeComma)):
                        if i == 0:
                            str = work[0:placeComma[i][0]].lstrip().rstrip()
                        elif i == len(placeComma)-1:
                            str = work[placeComma[i-1][1]:placeComma[i][0]].lstrip().rstrip()
                            self.list_words_workflow.append([idx,str])
                            str = work[placeComma[i][1]:].lstrip().rstrip()
                        else:
                            str = work[placeComma[i-1][1]:placeComma[i][0]].lstrip().rstrip()
                        self.list_words_workflow.append([idx,str])
            #Without "into"
            else:
                startb = -1
                for i in range(len(listPatternOb)):
                    pat = listPatternOb[i]
                    for match in re.finditer(pat,self.list_output[idx]):
                        startb = match.span()[0] + len(keyWordsO[i]) + 1
                        endb = match.span()[1]
                    if startb >=0:
                        str = self.list_output[idx][startb:endb].lstrip().rstrip()
                        if str[0].isalpha():
                            self.list_words_workflow.append([idx,str])
                        else:
                            self.list_words_workflow.append([idx,str[1:]])
                        break


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
