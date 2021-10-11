import re

from process import *

#Right now we're supposing that the workflow parameter is a string of the workflow and not the adress of the worklfow => this needs to be changed later on
class Workflow:
  def __init__(self, workflow):
    self.name = None
    #So here for example you would need to extract the worklow from the file
    self.workflow_string = workflow
    self.nextflow_initia = None
    #List of processes -> we initialise it as an empty list
    self.processes = []
    self.channels = []
    
  #Method that prints the worflow string
  def printWorkflow(self):
    print(self.workflow_string)

  #Method that checks if the initialisation :"#!/usr/bin/env nextflow" is present
  def checkInitia(self):
    word= "#!/usr/bin/env nextflow"
    if(self.workflow_string.find(word) >= 0):
      self.nextflow_initia = True
    else:
      self.nextflow_initia = False
      #Maybe trow Error
      print("The nextflow Initia is not present")

  #Method that removes "#!/usr/bin/env nextflow" from the string_workflow if present
  def removeInitia(self):
    word= "#!/usr/bin/env nextflow"
    if(self.nextflow_initia):
      self.workflow_string= self.workflow_string.replace(word, "")

  #Method that removes all the comments from the workflow
  def removeComments(self):
    #TODO
    None

  #Method that extracts the different processes from the workflow and sets them in the list of processes
  #We're gonna do it in a very rudamental way, cause to at least to my knowledge right now it works and it's not to complexe
  #We're just gonna look at it linearly and count the number of open and close '{}'
  #We're going to exploit the fact that a process is definied as process ... { .... } and right now we're just get the begin and end. Not looking at what's inside
  def extractProcesses(self):
    work = self.workflow_string
    list_process_start=[]
    #Getting the begining of the processes in the string
    for m in re.finditer("process", self.workflow_string):
      list_process_start.append(m.start())
    #For each process: we find it and add it to the list of processes
    for i, start in enumerate(list_process_start):
      start= list_process_start[i]
      #{} curly brackets
      count_curly = -1
      end = start
      while(count_curly != 0):
          if(work[end] == "{" and count_curly == -1):
              count_curly = 1
          elif(work[end] == "{"):
              count_curly += 1
          elif(work[end] == "}"):
              count_curly -= 1
          end += 1
      #This bit of code looks complicated but it's just adding the process already extarcted to the list of processes
      process = Process(self.workflow_string[start:end])
      process.extractProcess()
      self.processes.append(process)

  #Method that prints all the processes in the worflow
  def printProcesses(self):
    for p in self.processes:
      p.printProcess()

  #Method that prints all the names of the processe in the workflow
  def printProcessesName(self):
    for p in self.processes:
      p.printName()

  #Like the equivalent of the main => sets everything
  def extractWorflow(self):
    self.checkInitia()
    self.removeInitia()
    self.extractProcesses()
    #Do stuff
    
if __name__ == "__main__":
    print("I shoudn't be executed as a main")

