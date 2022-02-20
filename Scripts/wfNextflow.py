import os
from process import *
from typeMainDSL1 import *
from functionsProcess.toolFunction import *
import re
from pathlib import Path

"""
If two or more process have the same name in the workflows - give an index number
"""
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
        #Global Informations
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

        #Script Informations
        self.script_toolsNb = None
        self.script_toolsName = [] #list name tools
        self.script_toolsNbInWf = {}
        self.script_annotations = {}

        #Stub Informations
        self.stub_toolsNb = None
        self.stub_toolsName = [] #list tools
        self.stub_toolsNbInWf = {}
        self.stub_annotations = {}

        #Process Informations
        self.processNb = None
        self.processName = [] #list name 
        self.process = {} # dico : key name process and value tab : @ process
        self.processAnalyse = [] 

        #Name Process with tools used
        self.dicoProcessTools = {}
    
    #--------------------------------------------#
    def getNameFolder(self):
        return self.nameFolder

    def getToolsScript(self):
        return self.script_toolsName

    def getAnnotationsScript(self):
        return self.script_annotations

    def getAnnotationsStub(self):
        return self.stub_annotations

    def getProcess(self):
        return self.process

    def getTools(self):
        return self.script_toolsName + self.stub_toolsName

    def getProcessTools(self):
        return self.dicoProcessTools
        
    #--------------------------------------------#
    def extract(self):
        """
        Extract all Informations of the Workflow
        """
        nbErrors = 0
        errors = []
        ok = True
        for i in range (len(self.listFiles)): 
            urlfile = self.listFiles[i]
            study = urlfile.split('/')[-1]
            if study[0] != '.':
                nameFile = str(i) + '.nf'
                try: 
                    #Download file if we need:
                    try:
                        with open(nameFile): 
                            p = os.getcwd() + "/" + nameFile
                            fileSize = Path(p).stat().st_size
                            increment = 0
                            """while fileSize == 0 and increment != 2:
                                increment += 1
                                os.system('wget -q "' + urlfile + '" -O ' + nameFile)"""
                    except Exception as exc:
                        os.system('wget -q "' + urlfile + '" -O ' + nameFile)

                    #Extract and Analyse Process
                    file = TypeMainDSL1(nameFile, "", analyse=True)  #for the moment typeMainDSL1
                    file.initialise_basic_main()
                    file.find_processes()
                    process = file.get_processes()
                    for p in process:
                        if not p.goodForAnalyse():
                            ok = False
                    if ok:
                        self.processAnalyse.append(file.get_processes()) #already do extractProcess

                except Exception as exc:
                    nbErrors +=1
                    errors.append(exc)
                    print("ERROR in extractInfoWorkflow : " , exc, " ", self.listFiles[i] + " " + nameFile)
                    ok = False
        if nbErrors != 0:
            print("     NB errors :", nbErrors, "/",len(self.listFiles))
        
        if ok:
            #Add informations
            for p in self.processAnalyse:
                for i in range (len(p)):
                    #Process - Global
                    work = p[i]
                    name = work.getName()
                    name = findName(name, self.processName)
                    self.processName.append(name)
                    self.process.update({name:work})
                    tools = []
                    #Script
                    if work.getScript() != None:
                        nameCommands = work.getScript().getTools()
                        annot = work.getScript().getAnnotations()
                        for t in nameCommands:
                            if not t in self.script_toolsName:
                                self.script_toolsName.append(t)
                                
                        
                        for t in nameCommands:
                            string = ""
                            for i in range (len(t)):
                                string += t[i] + " "
                            if not string in self.script_toolsNbInWf:
                                self.script_toolsNbInWf.update({string:1})
                            else:
                                self.script_toolsNbInWf[string] += 1

                        for a in annot:
                            bioId = annot[a]['name']
                            if not bioId in self.script_annotations:
                                self.script_annotations.update({a:annot[a]})
                            if not bioId in tools:
                                tools.append(bioId)
                    #Stub
                    if work.getStub() != None:
                        nameCommands = work.getStub().getTools()
                        annot = work.getStub().getAnnotations()
                        for t in nameCommands:
                            if not t in self.stub_toolsName:
                                self.stub_toolsName.append(t)
                        
                        for t in nameCommands:
                            string = ""
                            for i in range (len(t)):
                                string += t[i] + " "
                            if not string in self.stub_toolsNbInWf:
                                self.stub_toolsNbInWf.update({string:1})
                            else:
                                self.stub_toolsNbInWf[string] += 1

                        for a in annot:
                            bioId = annot[a]['name']
                            if not bioId in self.stub_annotations:
                                self.stub_annotations.update({a:annot[a]})
                            if not bioId in tools:
                                tools.append(bioId)
                    self.dicoProcessTools.update({name:tools})
            self.processNb = len(self.processName)
            self.script_toolsNb = len(self.script_toolsName)
            self.stub_toolsNb = len(self.stub_toolsName)
            return True
        else: 
            return False


if __name__ == "__main__":
    print("I shouldn't be executed as a main")
