# Nextflow Analyzer
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022


from .commonFunction import *

"""
FIRST PART
"""
#List created from https://www.nextflow.io/docs/latest/process.html#directives
keyWordsD = ["accelerator", "afterScript", "beforeScript", "cache", "cpus", "conda", "container", "containerOptions", "clusterOptions", "disk",
            "echo", "errorStrategy", "executor", "ext", "label", "machineType", "maxErrors", "maxForks", "maxRetries", "memory", "module",
            "penv", "pod", "publishDir", "queue", "scratch", "stageInMode", "stageOutMode", "storeDir", "tag", "time", "validExitStatus"]

#Create Pattern
listPatternD = []
for words in keyWordsD:
    string = "([^,]\\n+\\s*" + words + "[^a-zA-Z0-9])"
    listPatternD.append(string)
    
"""
SECOND PART - Class
"""
class Directives:
    def __init__(self, strDir):
        self.directive_string = strDir
        self.list_directive = []
        self.list_qualifier = []

    def printDirectives(self):
        print(self.directive_string)
    
    def printListDirective(self):
        for string in self.list_directive:
            print(string)
    
    def numberDirectives(self):
        return len(self.list_directive)
    
    def getQualifier(self):
        return self.list_qualifier
    
    def getDirectives(self):
        return self.list_directive

    def extractQualifier(self):
        self.list_qualifier = extractQ(self.list_directive)
    
    def splitDirective(self):
        self.list_directive = splits(listPatternD, self.directive_string)

    def extractD(self):
        self.splitDirective()
        self.extractQualifier()

