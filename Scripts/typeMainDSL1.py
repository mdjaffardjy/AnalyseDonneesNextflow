import re
from typeMain import * 
from process_test import *
from function import *

class TypeMainDSL1(TypeMain):
    def __init__(self, address):
        super().__init__(address)
        self.processes=[]
        self.functions=[]
        #TODO
        #This attribute is temporary
        self.onComplete=None


    #===========================================
    #UTILITY METHODS
    #===========================================

    #Intermediate method that 'finds' the end of the process or functions, when we give the start position
    #So it follows the pattern 'process name {....}' or def name(..){...}
    def extract_curly(self, start):
        count_curly = 1
        end = start
        work= self.string
        while(count_curly != 0):
            if(work[end] == "{"):
                count_curly += 1
            elif(work[end] == "}"):
                count_curly -= 1
            end += 1
        return end

    #===========================================
    #METHODS FOR MANIPULATING PROCESSES
    #===========================================

    #Finds and adds the processes to the list of processes
    def find_processes(self):
        pattern= r'(process\s*\w*\s*{)'
        for match in re.finditer(pattern, self.string):
            #print(self.string[match.span()[0]:match.span()[1]])
            start= match.span()[0]
            end= self.extract_curly(match.span()[1])
            process= Process(self.string[start:end])
            process.extractProcess()
            self.processes.append(process)   
    
    #Print the names of the different processes
    def print_name_processes(self):
        for p in self.processes:
            p.printName()

    #Return the number of processes
    def get_nb_processes(self):
        return len(self.processes)

    #Print the different processes
    def print_processes(self):
        for i in range(len(self.processes)):
            print(self.processes[i].get_string())

    #Removes the proesses from the workflow string: this isn't really usefull outside the prototyping/developpement stage
    def format_processes(self):
        for p1 in self.processes:
            i=-1
            for p2 in self.processes:
                if(p1.get_name()==p2.get_name()):
                    i+=1
            if(i>0):
                p1.change_name(p1.get_name()+'_'+str(i))


        for i in range(len(self.processes)):
            self.string= self.string.replace(self.processes[i].get_string(), 'PROCESS DEF '+self.processes[i].get_name(), 1)


    #===========================================
    #METHODS FOR MANIPULATING CHANNELS
    #===========================================
    
    #Finds the channels and adds them to the list of Channels
    #TODO
    def find_channels(self):
        pattern_basic= r'((c|C)hannel[ \n]*\.)'




    #===========================================
    #METHODS FOR MANIPULATING FUNCTIONS
    #===========================================

    #Finds and adds the functions to the list of functions
    def find_functions(self):
        pattern= r'(def *\w* *\((\w*| *|,)*\)\s*{)'
        for match in re.finditer(pattern, self.string):
            #print(self.string[match.span()[0]:match.span()[1]])
            start= match.span()[0]
            end= self.extract_curly(match.span()[1])
            fun = Function(self.string[start:end])
            fun.initialise_function()
            self.functions.append(fun)
    
    #Print the names of the different functions
    def print_name_functions(self):
        for f in self.functions:
            f.print_name()

    #Return the number of functions
    def get_nb_functions(self):
        return len(self.functions)
    
    #Prints the different functions
    def print_functions(self):
        for f in self.functions:
            print('Function {} : '.format(f.get_name()))
            f.print_function()

    #Removes the functions from the workflow string: this isn't really usefull outside the prototyping/developpement stage
    def format_functions(self):
        for i in range(len(self.functions)):
            self.string= self.string.replace(self.functions[i].get_string(), 'FUNCTION DEF '+self.functions[i].get_name())

    #TODO 
    #For know we are just gonna put the string in an attribute (string) and not analyse it YET
    #My intuition right now is to create a subworkflow with the workflow.onComplete in it
    #Or maybe create a new class 
    #===========================================
    #METHODS FOR workflow.onComplete
    #TODO Do the same for workflow.onError
    #===========================================
    def temp_workflow_onComplete(self):
        pattern= r'(workflow.onComplete\s*{)'
        i=0
        for match in re.finditer(pattern, self.string):
            #This is just to test the fact that there isn't over one declaration
            i+=1
            if(i>1):
                raise Exception("More than one 'workflow.onComplete' found in the workflow")
            #Finding the pattern
            start= match.span()[0]
            end= self.extract_curly(match.span()[1])
            self.onComplete= self.string[start:end]
            #Replacing the declaration by a marker
            self.string= self.string.replace(self.onComplete, 'WORKFLOW ON_COMPLETE')
            


    #===========================================
    #GENERAL METHODS
    #===========================================

    #Saves the the worklfow string in a given address as a nextflow file
    def save_file(self, address= "/home/george/Bureau/TER/", name='formated_workflow'):
        myText = open(address+name+'.nf','w')
        myText.write(self.string)
        myText.close()

    #Supposong that remove comment works correctly
    #Initialise the basic stuff for a mainDSL1 type
    def initialise(self):
        self.initialise_basic_main()
        self.find_processes()
        self.find_functions()
        self.format_processes()
        self.format_functions()
        #TODO
        #This is temporary => need to update the method so that is does more!
        self.temp_workflow_onComplete()
        



#=================
#IF USED AS A MAIN
#=================
if __name__ == "__main__":
    #print("I shoudn't be executed as a main")
    m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/samba-master/main.nf")
    m.initialise()
    m.print_name_processes()

    m.save_file()
    #m.print_processes()

    #m.print_name_functions()
    #print(m.get_nb_functions())
    #m.print_file()


#TODO List
# - IMPORTANT!!! Channels can appear in functions!! need to think about how to deal with that ! => Might not be as important as originally though
# - Think about how to deal with channels and functions
# - And to link everything together after
    