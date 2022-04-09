from os import listdir
from .commonFunction import *
import re
from .channel import *

"""
FIRST PART
""" 
def endPairs(txt,idx,s):
    count_curly = 1
    end = idx
    while(count_curly != 0):
      if(txt[end] == s[0]):
        count_curly += 1
      elif(txt[end] == s[1]):
        count_curly -= 1
      end += 1
    return end

def findPairs(txt, symbole):
    tab = []
    for i in range (len(txt)):
      if txt[i] == symbole[0]:
        end = endPairs(txt,i+1, symbole)
        tab.append([i,end])
    return tab

def prepare(txt):
    work = txt
    symbole = [['{', '}'], ['(', ')']]
    for s in symbole:
      tab = findPairs(txt, s)
      for i in range (len(tab)):
        if s[0] == '{' and i ==0:
          None
        else:
          start = tab[i][0]
          end = tab[i][1]
          change = txt[start:end].replace(" ", "")
          change = change.split()
          change = " ".join(change)
          work = work.replace(txt[start:end], change)
    return "\n" + work  

def function(tabPa, tabPo, tabA):
    for i in range (len(tabPa)):
        for p in tabPo:
            if p < tabPa[i][0] or tabPa[i][1]<p:
                return False
        for a in tabA:
            if a < tabPa[i][0] or tabPa[i][1]<a:
                return False
    return True

#List created from https://www.nextflow.io/docs/latest/process.html#inputs
keyWordsI = ['val', 'env', 'file', 'path', 'stdin', 'tuple', 'each', 'set']

#Create Pattern
listPatternIb = []
for words in keyWordsI:
    string = "(" + words + "(\s+|\(|\{|\[)+\w+)"
    listPatternIb.append(string)
    
listPatternI = []
for words in keyWordsI:
    string = "([^,]\\n+\\s*" + words + "[^a-zA-Z0-9])"
    listPatternI.append(string)

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
        self.list_input = splits(listPatternI, self.input_string)

    def extractQualifier(self):
        self.list_qualifier = extractQ(self.list_input)

    def extractName(self):
        pattern = r'(\sfrom\s.*$)'
        for i in range (len(self.list_input)):
            w = prepare(self.list_input[i])
            w = w.strip()
            start = -1
            #Find if we have the word 'from'
            for match in re.finditer(pattern, w):
                start = match.span()[0] + len("from")+2
                end = match.span()[1]
            
            #If we have the word from
            if start != -1:
                string = w[start:end].lstrip().rstrip()
                
                patParenthesis = r'(\(.*\))'
                tabP = []
                for match in re.finditer(patParenthesis,string):
                    tabP.append([match.span()[0],match.span()[1]])
                    
                tabIdxPoints = []
                tabIdxAccolade = []
                for s in range (len(string)):
                    if string[s] == '.':
                        tabIdxPoints.append(s)
                    if string[s] == '{':
                        tabIdxAccolade.append(s)
                
                #Just One word
                if len(tabP) == 0 and len(tabIdxPoints) == 0 and len(tabIdxAccolade) == 0:
                    inputs = string.split()[0]
                    self.list_words_workflow.append([i, inputs])
                    pass
                
                #Function
                elif len(tabP) > 0 and function(tabP,tabIdxPoints,tabIdxAccolade):
                    work = string[tabP[0][0]+1:-1]
                    wb = work.split(',')
                    types = string[:tabP[0][0]]
                    if not types in keyWordsI:
                        for wt in wb:
                            ok = False
                            for s in wt:
                                if s == '.' and not ok:
                                    channel = Channel('',wt)
                                    channel.initialise_channel()
                                    if len(channel.get_gives()) != 0:
                                        print("Channel bizarre dans extraction nameInputs")
                                    
                                    tabOrigin = channel.get_origin()
                                    for j in range(len(tabOrigin)):
                                        if tabOrigin[j][1] == 'P':
                                            self.list_words_workflow.append([i,tabOrigin[j][0]])
                                            ok = True
                            if not ok:
                                self.list_words_workflow.append([i,wt])
                #Channel
                else :
                    channel = Channel('',string)
                    channel.initialise_channel()
                    if len(channel.get_gives()) != 0:
                        print("Channel bizarre dans extraction nameInputs")
                    tabOrigin = channel.get_origin()
                    for j in range(len(tabOrigin)):
                        if tabOrigin[j][1] == 'P':
                            self.list_words_workflow.append([i,tabOrigin[j][0]])
                    pass
                
            #No key word "from"
            else: 
                for j in range (len(listPatternIb)):
                    pat = listPatternIb[j]
                    for match in re.finditer(pat,w):
                        startb = match.span()[0] + len(keyWordsI[j]) + 1
                        endb = match.span()[1]
                        if startb >=0:
                            string = w[startb:endb].lstrip().rstrip()
                            if string[0].isalpha():
                                if not string in keyWordsI:
                                    self.list_words_workflow.append([i,string])
                                pass
                            else:
                                if not string[1:] in keyWordsI:
                                    self.list_words_workflow.append([i,string[1:]])
                                pass 

    def extractI(self):
        self.splitInput()
        self.extractQualifier()
        self.extractName()

    
if __name__ == "__main__":
    print("I shouldn't be executed as a main")
