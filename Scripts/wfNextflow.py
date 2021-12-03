from os import error
from process import *
from typeMainDSL1 import *
from functionsProcess.toolFunction import *
import re

def findName(name, tab):
	numbers = 0
	nameWithoutNumbers = name
	if not name in tab:
		return name
	else:
		pat = r'(\d+)'
		for match in re.finditer(pat,name):
			numbers = name[match.span()[0]: match.span()[1]]
			numbers = int(numbers)
			nameWithoutNumbers = name[0:match.span()[0]]
		test = nameWithoutNumbers + str(numbers+1) 
		return findName(test, tab)

class Nextflow_WF:
    def __init__(self,url,listFiles):
        self.listFiles = listFiles

        self.url = url  
        self.name = "todo"

        self.toolsNb = None
        self.toolsName = [] #list tools
        self.toolsNbInWf = {}
        self.annotations = {}

        self.processNb = None
        self.processName = [] #list name 
        self.process = {} #idea : dico : key name process and value tab : @ process
        self.processAnalyse = [] 

    def getTools(self):
        return self.toolsName

    def getAnnotations(self):
        return self.annotations
        
    def extract(self):
        #Add first ectract process of the file
        nbErrors = 0
        errors = []

        for i in range (len(self.listFiles)):
            #print(self.listFiles[i])
            try:
                file = TypeMainDSL1(self.listFiles[i]) #for the moment typeMainDSL1
                file.initialise()
                self.processAnalyse.append(file.get_process()) #already does extractProcess
            except Exception as exc:
                nbErrors +=1
                errors.append(exc)
        print("NB errors :", nbErrors)
        #print(errors)

        for p in self.processAnalyse:
            for i in range (len(p)):
                work = p[i]
                name = work.getName()
                
                name = findName(name, self.processName)
                self.processName.append(name)
                self.process.update({name:work})

                nameTools = work.getScript().getTools()
                annot = work.getScript().getAnnotations()

                for t in nameTools:
                    if not t in self.toolsName:
                        self.toolsName.append(t)
                
                for t in nameTools:
                    string = ""
                    for i in range (len(t)):
                        string += t[i] + " "
                    if not string in self.toolsNbInWf:
                        self.toolsNbInWf.update({string:1})
                    else:
                        self.toolsNbInWf[string] += 1

                for a in annot:
                    bioId = annot[a]['name']
                    if not bioId in self.annotations:
                        self.annotations.update({a:annot[a]})

        self.processNb = len(self.processName)
        self.toolsNb = len(self.toolsName)

        #print(self.processName)


if __name__ == "__main__":
    print("I shouldn't be executed as a main")