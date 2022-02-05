from turtle import st
from functionsProcess.commonFunction import *
import re
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
        listEND = []
        pattern = r'(\sfrom\s.*$)'
        for i in range (len(self.list_input)):
            w = prepare(self.list_input[i])
            start = -1
            #Find if we have the word 'from'
            for match in re.finditer(pattern, w):
                start = match.span()[0] + len("from")+2
                end = match.span()[1]
            if start > -1:
                #we have from
                string = w[start:end].lstrip().rstrip()
                
                patE = r'( )'
                s1 = 0
                e1 = end
                for match in re.finditer(patE,string):
                    pat = [r'(\(.*\))', r'(\[.*\])', r'({.*\})']
                    tabNo = []
                    for p in pat:
                        for m in re.finditer(p, string):
                            tabNo.append([m.span()[0], m.span()[1]])
        
                    if e1 > match.span()[0]:
                        e1 = match.span()[0]
                string = string[s1:e1]
                nbPoints = 0
                nbParenthesis = 0
                nbAccolade = 0
                for l in string:
                    if l == '.':
                        nbPoints +=1
                    elif l == '(':
                        nbParenthesis +=1
                    elif l == '{':
                        nbAccolade += 1
                if nbPoints == 0 and nbParenthesis == 0 and nbAccolade == 0:
                    listEND.append([i, string])
                    pass
                
                elif nbParenthesis > 0 and nbPoints == 0 and nbAccolade == 0:
                    s = ""
                    patPa = r'(\([^.]*\))'
                    for match in re.finditer(patPa, string):
                        s0 = match.span()[0]+1
                        e0 = match.span()[1]-1
                    listEND.append([i, string[s0:e0]])
                    pass
                
                elif nbPoints > 0 and nbParenthesis > 0:
                
                    patPa = r'(\([^.]*\))'
                    for match in re.finditer(patPa, string):
                        s0 = match.span()[0]
                        s1 = match.span()[1]
                        wordSplit = string[s0:s1].split(",")
                        for word in wordSplit:
                            sf = ""
                            add = False
                            for s in word:
                                if s.isalpha() or s == "_" or s=="-":
                                    sf += s
                            if len(sf) == 0:
                                #prendre le premier mot
                                end = ""
                                for s in string:
                                    if s != '.':
                                        end += s
                                    elif s == '.':
                                        add = True
                                        listEND.append([i,end])
                                        pass
                                if not add:
                                    listEND.append([i,end])
                                    pass
                                
                            else:
                                #prendre le mot entre ()
                                listEND.append([i,sf])
                                pass
                
                elif nbPoints > 0 and nbAccolade > 0:
                    end = ""
                    for s in string:
                        if s != '.':
                            end += s
                        if s == '.':
                            listEND.append([i,end])
                            pass
                    pass
                
                elif nbPoints > 0 and nbParenthesis == 0 and nbAccolade == 0:
                    listEND.append([i,string])
                    """end = ""
                    for s in string:
                        if s != '.':
                            end += s
                        elif s == '.':
                            listEND.append([i,end])
                            pass"""
                
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
                                    listEND.append([i,string])
                                pass
                            else:
                                if not string[1:] in keyWordsI:
                                    listEND.append([i,string[1:]])
                                pass                
        #Clean
        name = []
        for t in listEND:
            n = t[1]
            if not n in name:
                self.list_words_workflow.append(t)
                name.append(n)

    def extractI(self):
        self.splitInput()
        self.extractQualifier()
        self.extractName()

    
if __name__ == "__main__":
    print("I shouldn't be executed as a main")
