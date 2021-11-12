from directive import *
from input import *
from output import * 
from when import * 
from script import *
from stub import *

import re
"""
FIRST PART : 

Declaration of global variable  
"""

#List de pattern
#Can be dvlp (dico)
listPattern = [r'(input\s*:)', r'(output\s*:)', r'(when\s*:)', r'(script\s*:)', r'(shell\s*:)', 
                      r'(exec\s*:)',r'(""")', r"(''')", r'(\n+\s*".*"\n)', r"(\n+\s*'.*'\n)", r'(stub\s*:)']
 
"""
SECOND PART - Class
"""

class Process:
  def __init__(self, process):
    #We suppose that process is a string of the process
    self.process_string = process
    #We are going to extract the informations from this variable and clean it when we finish to study a part
    self.process_work = process

    self.name = None
    self.directive = None
    self.input = None
    self.output = None 
    self.when = None
    self.script = None
    self.stub = None
    

  #Function which find the last } 
  def endProcess(self):
    patternEnd = r'(})'
    end = 0
    for match in re.finditer(patternEnd, self.process_work):
      if match.span()[0] > end:
        end = match.span()[0]
    return end

  #Method that prints the process as a string
  def printProcess(self):
    print(self.process_string)

  # ------------------------- NAME --------------------------#
  #Method that extracts the name of the process
  def extractName(self):
    #Pattern "Start" 
    patternStart = r'(process\s)'
    #Pattern "End"
    patternEnd = r'({)'
    #Find where is the first patternStart
    start = self.endProcess()
    for match in re.finditer(patternStart, self.process_string):
      if match.span()[1] < start:
        start = match.span()[1]

    #Find where is the first {
    end = self.endProcess()
    for match in re.finditer(patternEnd, self.process_string):
      if match.span()[0] < end:
        end = match.span()[0]

    #The name is between the pattern start and end 
    #And we delete the " " at the beginning and at the end
    self.name = self.process_string[start:end].lstrip().rstrip()

  #Change the name of the process (if the process if defined in a if else)
  def changeName(self, newName):
    self.name = newName
 
  #Print the name of the process
  def printName(self):
    print(self.name)
  
  

  # ------------------------- DIRECTIVES --------------------------#
  #Extract directives
  #Always at the beginning of the Process
  def extractDirective(self):
    #Start 
    patternStart = r'({)'
    start = self.endProcess()
    for match in re.finditer(patternStart, self.process_work):
      if match.span()[1] < start:
        start = match.span()[1]

    #Check if we don't have a process empty (with no directives ...)
    study = self.process_work[start: self.endProcess()].lstrip()
    if (start != self.endProcess()) and len(study) != 0:
      #End
      end = self.endProcess()
      for pattern in listPattern:
        for match in re.finditer(pattern, self.process_work):
          #Check if the next step is after the step we want to study + we want the first one just after
          if (match.span()[0] < end) and (match.span()[0] > start):
            end = match.span()[0]
      string =  self.process_work[start:end].lstrip().rstrip()
      if len(string) != 0:
        #Add the informations into self.directive
        studyDirectives = Directives(string)
        studyDirectives.extractD()
        self.directive = studyDirectives
        #Remove what we were study (going to have a string without all directives)
        self.process_work = self.process_work.replace(self.process_work[start:end].lstrip().rstrip(), "")

  def printDirectives(self):
    if self.directive == None:
      print("No Directives")
    else:
    #For the moment : list of directives
      self.directive.printListDirective()

  def numberDirectives(self):
    return self.directive.numberDirectives()

  

  # ------------------------- INPUTS --------------------------#
  #Method that extracts the input 
  def extractInput(self):
    #Start 
    patternStart = r'(input\s*:)'
    start= [-1,-1]
    for match in re.finditer(patternStart, self.process_work):
      start = match.span()
    #Verify if our process contains the patternStart
    if start[1] != -1:
      #End
      end = self.endProcess()
      for pattern in listPattern:
        if pattern != patternStart:
          for match in re.finditer(pattern, self.process_work):
            if (match.span()[0] < end) and (match.span()[0] > start[1]):
              end = match.span()[0]
      string =  self.process_work[start[1]:end].lstrip().rstrip()
      if len(string) != 0:
        studyInput = Inputs(string)
        studyInput.extractI()
        self.input = studyInput
        self.process_work = self.process_work.replace(self.process_work[start[0]:end].lstrip().rstrip(), "")
      
  #Print the input
  def printInput(self):
    if self.input == None:
      print("No Inputs")
    else:
      self.input.printListInput() 

  def numberInputs(self):
    return self.input.numberInputs()  

  # ------------------------- OUTPUTS --------------------------#
  #Method that extracts the output 
  def extractOutput(self):
    #Start 
    patternStart = r'(output\s*:)'
    start= [-1,-1]
    for match in re.finditer(patternStart, self.process_work):
      start = match.span()
    if start[1] != -1:
      #End
      end = self.endProcess()
      for pattern in listPattern:
        if pattern != patternStart:
          for match in re.finditer(pattern, self.process_work):
            if (match.span()[0] < end) and (match.span()[0] > start[1]):
              end = match.span()[0]
      string = self.process_work[start[1]:end].lstrip().rstrip()
      if len(string) != 0:
        studyOutput = Outputs(string)
        studyOutput.extractO()
        self.output = studyOutput
        self.process_work = self.process_work.replace(self.process_work[start[0]:end].lstrip().rstrip(), "")
    
  #Print the input
  def printOutput(self):
    if self.output == None:
      print("No Outputs")
    else:
      self.output.printListOutput()

  def numberOutputs(self):
    return self.output.numberOutputs()

  

  # ------------------------- WHEN --------------------------#
  #Extract When
  def extractWhen(self):
    #Start 
    patternStart = r'(when\s*:)'
    start= [-1,-1]
    for match in re.finditer(patternStart, self.process_work):
      start = match.span()
    if start[1] != -1:
      #End
      end = self.endProcess()
      for pattern in listPattern:
        if pattern != patternStart:
          for match in re.finditer(pattern, self.process_work):
            #We check if the next step is after the step we want to study + we want the first one just after
            if (match.span()[0] < end) and (match.span()[0] > start[1]):
              end = match.span()[0]
      string = self.process_work[start[1]:end].lstrip().rstrip()
      if len(string) != 0:
        studyWhen = When(string)
        #studyWhen.extractW()
        self.when = studyWhen
        self.process_work = self.process_work.replace(self.process_work[start[0]:end].lstrip().rstrip(), "")

  def printWhen(self):
    if self.when == None:
      print("No When")
    else:
      self.when.printWhen()
    
 

  # ------------------------- SCRIPT --------------------------#
  #Always at then end - finish a process
  def extractScript(self):
    #Start 
    patternStart = [r'(script\s*:)', r'(shell\s*:)', r'(exec\s*:)', r'(""")', r"(''')",r'(\n+\s*".*"\n)', r"(\n+\s*'.*'\n)"]
    start = [-1,self.endProcess()]
    patternMatch = ""
    for pattern in patternStart:
      for match in re.finditer(pattern, self.process_work):
        if match.span()[1] < start[1]:
          start = match.span()
          patternMatch = pattern

    #Little script
    if patternMatch == r'(\n+\s*".*"\n)' or patternMatch ==  r"(\n+\s*'.*'\n)":
        string =  self.process_work[start[0]:start[1]].lstrip().rstrip()
        studyScript = Script(string)
        studyScript.extractS()
        self.script = studyScript

        self.process_work = self.process_work.replace(self.process_work[start[0]:start()[1]].lstrip().rstrip(), "")


    elif start[1] != self.endProcess():
      #End
      end = self.endProcess()
      for pattern in listPattern:
        if not pattern in patternStart:
          for match in re.finditer(pattern, self.process_work):
            if (match.span()[0] < end) and (match.span()[0] > start[1]):
              end = match.span()[0]
      string =  self.process_work[start[1]:end].lstrip().rstrip()
      if len(string) != len("\n"):
        studyScript = Script(string)
        studyScript.extractS()
        self.script = studyScript

        self.process_work = self.process_work.replace(self.process_work[start[0]:end].lstrip().rstrip(), "")

  def printScript(self):
    if self.script  == None:
      print("No script")
    else:
      self.script.printString()

  

  # ------------------------- STUB --------------------------#
  # To improve
  def extractStub(self):
    patternAccepted =  [r'(""")', r"(''')",r'(\n+\s*".*"\n)', r"(\n+\s*'.*'\n)"]
    #Start 
    patternStart = r'(stub\s*:)'
    start= [-1,-1]
    for match in re.finditer(patternStart, self.process_work):
      start = match.span()      
    if start[1] != -1:
      #End
      end = self.endProcess()
      for pattern in listPattern:
        if pattern != patternStart and not (pattern in patternAccepted):
          for match in re.finditer(pattern, self.process_work):
            if (match.span()[0] < end) and (match.span()[0] > start[1]):
              end = match.span()[0]
      string = self.process_work[start[1]:end].lstrip().rstrip()
      if len(string) != 0:
        studyStub = Stub(string)
        studyStub.extractS()
        self.stub = studyStub

        self.process_work = self.process_work.replace(self.process_work[start[0]:end].lstrip().rstrip(), "")

  def printStub(self):
    if self.stub == None:
      print("No stub")
    else:
      self.stub.printString()

  

  #Like the main => does everything to extract the informations
  def extractProcess(self):
    """
    Extract the different parts of a process
    Begin with Name and directives (always at the beginning)
    After : work on the other which need key words like input, output ...
    Finish with Script which can have different forms
    """
    self.extractName()
    self.extractDirective()
    self.extractInput()
    self.extractOutput()
    self.extractWhen()
    self.extractStub()
    self.extractScript()

    """
    Verify if all the things were analysed - if self.process_work est vide
    """
    self.process_work = self.process_work.replace("process", "")
    self.process_work = self.process_work.replace(self.name, "")
    self.process_work = self.process_work.replace("{", "")
    self.process_work = self.process_work.replace("}", "")
    self.process_work = self.process_work.lstrip().rstrip()
    if len(self.process_work) != 0:
      print("ERROR - Something is wrong ! - self.process_work is not empty : ", self.process_work)
    #To continued

  def getName(self):
    return self.name
  def getDirective(self):
    return self.directive
  def getInput(self):
    return self.input
  def getOutput(self):
    return self.output 
  def getWhen(self):
    return self.when
  def getScript(self):
    return self.script
  def getStub(self):
    return self.stub

  def getAll(self):
    return [self.getName(), self.getDirective(), self.getInput(), self.getOutput(), 
                                  self.getWhen(), self.getScript(), self.getStub()]

  def printNumberInformations(self):
    if self.directive != None:
      print("Directives :", self.numberDirectives())
      self.directive.printQualifier()
  
    if self.input != None:
      print("Inputs : ", self.numberInputs())
      self.input.printQualifier()

    if self.output != None:
      print("Outputs :", self.numberOutputs())
      self.output.printQualifier()

    if self.script != None:
      print("Language Script:", self.script.printLanguage())

    if self.stub != None:
      print("Language Stub:", self.stub.printLanguage())

  def extractNumbersInformations(self):
    nD, nI, nO = 0,0,0
    if self.directive != None:
      nD = self.numberDirectives()

    if self.input != None:
      nI = self.numberInputs()
      
    if self.output != None:
      nO = self.numberOutputs()

    return nD, nI, nO
  
  def extractInformations(self):
    d,i,o = {}, {}, {}
    if self.directive != None:
      d = self.directive.getQualifier()

    if self.input != None:
      i = self.input.getQualifier()

    if self.output != None:
      o = self.output.getQualifier()
    
    return d,i,o

  def printInformations(self):
    print("----NAME PROCESS----")
    self.printName()
    print("  ")
    print("----DIRECTIVES----")
    self.printDirectives()
    print("  ")
    print("----INPUTS----")
    self.printInput()
    print("  ")
    print("----OUTPUTS----")
    self.printOutput()
    print("  ")
    print("----WHEN----")
    self.printWhen()
    print("  ")
    print("----SCRIPT----")
    self.printScript()
    print("   ")
    print("----STUB----")
    self.printStub()
    print("  ")
    print("----NUMBERS----")
    self.printNumberInformations()
    
if __name__ == "__main__":
    print("I shouldn't be executed as a main")




  