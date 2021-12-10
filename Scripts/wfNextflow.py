import os
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
    def __init__(self,url,listFiles, nameWf, nameFolder, creation_date, actualDate, last_push, owner, description, forks,stars):
        self.url = url
        self.listFiles = listFiles
        self.name = nameWf
        self.nameFolder = nameFolder
        self.creationDate = creation_date
        self.crawlerDate = actualDate 
        self.lastPush = last_push
        self.owner = owner
        self.description = description
        self.forks = forks
        self.stars = stars 

        self.toolsNb = None
        self.toolsName = [] #list tools
        self.toolsNbInWf = {}
        self.annotations = {}

        self.processNb = None
        self.processName = [] #list name 
        self.process = {} # dico : key name process and value tab : @ process
        self.processAnalyse = [] 
    
    def getNameFolder(self):
        return self.nameFolder

    def getTools(self):
        return self.toolsName

    def getAnnotations(self):
        return self.annotations

    def getProcess(self):
        return self.process
        
    def extract(self):
        nbErrors = 0
        errors = []
        for i in range (len(self.listFiles)): 
            urlfile = self.listFiles[i]
            patSlash = r'(/)'
            last = 0
            for match in re.finditer (patSlash, urlfile):
                if match.span()[1] > last:
                    last= match.span()[1]
            nameFile = urlfile[last:]
    
            try: 
                #Download file if we need:
                try:
                    with open(nameFile): pass
                except IOError:
                    os.system("wget -q " + urlfile)

                file = TypeMainDSL1(nameFile)  #for the moment typeMainDSL1
                #file.initialise()
                file.initialise_basic_main()
                file.find_processes()
                self.processAnalyse.append(file.get_process()) #already does extractProcess

                #os.system("rm " + nameFile)

            except Exception as exc:
                nbErrors +=1
                errors.append(exc)
                print(exc, " ", self.listFiles[i])
        if nbErrors != 0:
            print("     NB errors :", nbErrors, "/",len(self.listFiles))
            #print(errors)
        
        for p in self.processAnalyse:
            for i in range (len(p)):
                work = p[i]
                name = work.getName()
                name = findName(name, self.processName)
                self.processName.append(name)
                self.process.update({name:work})

                if work.getScript() != None:
                    nameTools = work.getScript().getTools()
                    annot = work.getScript().getAnnotations()
                    #print(nameTools)
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

if __name__ == "__main__":
    print("I shouldn't be executed as a main")