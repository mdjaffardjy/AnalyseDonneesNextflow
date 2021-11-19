from process import *

import re

"""
FIRST PART
"""
# To improve
keyWordsD = ["accelerator", "afterScript", "beforeScript", "cache", "cpus", "conda", "container", "containerOptions", "clusterOptions", "disk",
            "echo", "errorStrategy", "executor", "ext", "label", "machineType", "maxErrors", "maxForks", "maxRetries", "memory", "module",
            "penv", "pod", "publishDir", "queue", "scratch", "stageInMode", "stageOutMode", "storeDir", "tag", "time", "validExitStatus"]

listPatternD = []
for words in keyWordsD:
    str = "([^,]\\n+\\s*" + words + "[^a-zA-Z0-9])"
    listPatternD.append(str)

"""
SECOND PART - Class
"""
class Directives:
    def __init__(self, strDir):
        self.directive_string = strDir
        self.list_directive = []
        self.qualifier = {}

    def printDirectives(self):
        print(self.directive_string)
    
    def printListDirective(self):
        for str in self.list_directive:
            print(str)
    
    def numberDirectives(self):
        return len(self.list_directive)
    
    def getQualifier(self):
        return self.qualifier
    
    def getDirectives(self):
        return self.list_directive

    def splitDirectives(self):
        work = "a \n" + self.directive_string
        index = []
        for pattern in listPatternD:
            for match in re.finditer(pattern, work):
                index.append(match.span()[0]+1)
        index.sort()
        for i in range (len(index)):
            if i == len(index)-1:
                directive = work[index[i]:].lstrip().rstrip()
            else:   
                directive = work[index[i]:index[i+1]].lstrip().rstrip()

            antiSlash = []
            for match in re.finditer(r"(\\)", directive):
                    antiSlash.append(match.span())
            antiSlash.sort(reverse = True)
            for j in range(len(antiSlash)):
                directive = directive.replace(directive[antiSlash[j][0]:antiSlash[j][1]], " ")
            directive =" ".join(directive.split())
            self.list_directive.append(directive)

    def analyseQualifier(self):
        for str in self.list_directive:
            cut = re.split("[^\w]", str)
            key = cut[0]
            if key in self.qualifier:
                self.qualifier[key] += 1
            else:
                self.qualifier.update({key:1})

    def extractD(self):
        self.splitDirectives()
        self.analyseQualifier()

if __name__ == "__main__":
    print("I shouldn't be executed as a main")