

class Process:
  def __init__(self, process):
    #We suppose that process is a string of the process
    self.process_string = process
    self.name = None
    #Gonna be a list of inputs -> don't know the form of the inputs yet
    #Same for outputs
    self.input = []
    self.output = []
    #Don't really know what these are gonna be yet
    self.condition = None
    self.script = None

  #Method that prints the process as a string
  def printProcess(self):
    print(self.process_string)

  #Method that extracts the name of the process
  #We've written this in a very simple way, which is effective and not complexe but not very pretty
  def extractName(self):
    p = "process"
    start= self.process_string.find(p)+ len(p)
    end= start
    while(self.process_string[end]!='{'):
        end+=1
    word= self.process_string[start:(end)].strip()
    self.name = word

  #Prints the name of the process
  def printName(self):
    print(self.name)

  def get_name(self):
    return self.name

  def get_string(self):
    return self.process_string


  #Like the main => does everything to extract the informations
  def extractProcess(self):
    self.extractName()
    #Do stuff
    None


if __name__ == "__main__":
    print("I shoudn't be executed as a main")