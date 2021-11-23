import re
from typeMain import * 
from process_test import *
from function import *
from channel import *
from utility import *

class TypeMainDSL1(TypeMain):
    def __init__(self, address):
        super().__init__(address)
        self.processes=[]
        self.functions=[]
        self.channels=[]
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
    
    def get_end_channel(self, start, curly_count=0, parenthesis_count=0):
        index= start
        while(index<len(self.string)):

            if(self.string[index]=='{'):
                curly_count+=1
            elif(self.string[index]=='}'):
                curly_count-= 1
            elif(self.string[index]=='('):
                parenthesis_count+= 1
            elif(self.string[index]==')'):
                parenthesis_count-= 1

            elif(curly_count==0 and parenthesis_count==0):

                if(self.string[index]==':'):
                    return index
                elif(self.string[index]=='\n' and get_next_element_caracter(self.string, index)[0]!='.'):
                    return index
            
            index+=1
        #raise Exception("Major Problem in get_end_channel: out of range")
        return index 


    def get_channel(self, id):
        for c in self.channels:
            if id== c.get_id():
                return c
        raise Exception('Channel not in list of channels')

    
    def extract_branches(self, start, end):
        string= self.string[start:end]
        tab=[]
        pattern= r'(\w+)\s*:'
        for match in re.finditer(pattern, string):
            tab.append(match.group(1))
        return tab

    #TODO Check to see if multiMap works well => haven't tested yet
    def get_added_operators(self):
        tab=[]
        pattern =r'.(branch|multiMap)\s*{'
        for match in re.finditer(pattern, self.string):
            #print(match.span(0))
            start=match.span(0)[0]
            end= extract_curly(self.string, match.span(0)[1])
            #print(string[start:end])
            tab+= self.extract_branches(start, end)
        return tab


    #Method pas parfait => workflow.CHANNEL_54 dans eager
    #Mais c'est pas très grave car on prend 'plus' qu'on a besoin
    #Collect les faux positifs enfaite mais pas très grave
    def extract_channels(self):
        
        #=================================================================
        #PART ZERO: BEFORE WE START WE NEED TO EXTRACT THE ADDED OPERATORS CREATED WITH BRANCH 
        #=================================================================
        ope= self.get_added_operators()
        added= '|'.join(ope)
        if added != '':
            added='|'+added
        #print(added)
        for o in ope:
            pattern=r'\.\s*('+o+')\s*\.'
            for match in re.finditer(pattern, self.string):
                word=match.group(0)
                self.string= self.string.replace(word, '.{}().'.format(o), 1)

        #=================================================================
        #FIRST PART: WE EXTRACT THE ONES WITH THE WORD CHANNEL 
        #=================================================================
        pattern= r'[^\w]((C|c)hannel\s*\.)'
        index=1
        for match in re.finditer(pattern, self.string):
            start= match.span(1)[0]
            end= self.get_end_channel(start)
            code= self.string[start:end]
            #print(code)
            #print(code)
            name= 'CHANNEL_'+str(index)
            self.channels.append(Channel(name, code))
            index+=1
        for c in self.channels:
            #print(c.get_id(), c.get_string())
            self.string= self.string.replace(c.get_string(), c.get_id(), 1)
        
        #=================================================================
        #SECOND PART: WE EXTRACT THE OTHER ONES 
        #=================================================================
        operations= 'distinct|filter|first|last|randomSample|take|unique|until|buffer|collate|collect|flatten|flatMap|groupBy|groupTuple|map|reduce|toList|toSortedList|transpose|splitCsv|splitFasta|splitFastq||splitText|cross|collectFile|combine|concat|join|merge|mix|phase|spread|branch|choice|multiMap|into|separate|tap|count|countBy|min|max|sum|toInteger|close|dump|ifEmpty|print|println|set|view|create|empty|from|fromPath|fromFilePairs|fromSRA|of|value|watchPath|subscribe'+added
        pattern= r'(\w+)\s*\.\s*('+operations+')\s*({|\()'
        tab=[]
        for match in re.finditer(pattern, self.string):
            if match.group(1)!='workflow':
                #print(match.group(0))
                start= match.span(0)[0]
                if(self.string[match.span(0)[1]-1]=='('):
                    end= self.get_end_channel(match.span(0)[1], 0, 1)
                elif(self.string[match.span(0)[1]-1]=='{'):
                    end= self.get_end_channel(match.span(0)[1], 1, 0)
                else: 
                    raise Exception("Don't know what i'm looking at..")
                name= 'CHANNEL_'+str(index)
                code= self.string[start:end]
                self.channels.append(Channel(name, code))
                index+=1
        for c in self.channels:
            #print(c.get_id(), c.get_string())
            self.string= self.string.replace(c.get_string(), c.get_id(), 1)

        #=================================================================
        #THIRD PART: LINK THE TYPES CHANNEL THAT ARE DEFINED AS ... = CHANNEL_ID
        #=================================================================
        #TODO ADD the case (var1, var2) or (var1, var2, ..., varX)
        pattern= r'(\w+)\s*=\s*(CHANNEL_\d+)'
        for match in re.finditer(pattern, self.string):
            #print(match.group(0),match.group(1), match.group(2))
            c= self.get_channel(match.group(2))
            c.set_gives(match.group(1))
            self.string= self.string.replace(match.group(0), match.group(2), 1)

        #=================================================================
        #FOURTH PART: INITIALISE THE CHANNELS
        #=================================================================
        for c in self.channels:
            c.initialise_channel()

        #return string, channels

    def save_channels(self, address= "/home/george/Bureau/TER/", name='channels'):
        myText = open(address+name+'.nf','w')
        for c in self.channels:
            myText.write(str(c.get_gives())+' <- '+c.get_string()+'\n\n')
        myText.close()





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
        self.format_processes()
        self.extract_channels()
        #We extract the channels first since channels can be declared in functions
        self.find_functions()
        self.format_functions()
        
        self.temp_workflow_onComplete()
        



#=================
#IF USED AS A MAIN
#=================
if __name__ == "__main__":
    #print("I shoudn't be executed as a main")
    m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/samba-master/main.nf")
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/eager-master/main.nf")
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/hic-master/main.nf")
    #Still need to look into sarek
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/sarek-master/main.nf")
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/smrnaseq-master/main.nf")
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/metaboigniter-master/main.nf")
    m.initialise()
    m.print_name_processes()

    m.save_file()
    m.save_channels()
    #m.print_processes()

    #m.print_name_functions()
    #print(m.get_nb_functions())
    #m.print_file()


#TODO List
# - And to link everything together after
# - Remove comments is still not perfect=> see metaboigniter
# - workflow.onError
# - Finish ifs and do the ... = dsfdsf ? dsfdsf : dsfsdfsd case
#\w+\s*=\s*[\w\.(),\"'{}\[\]+-]+\s*\?\s*[\w\.(),\"'{}\[\]+-]+\s*\:\s*[\w\.(),\"'{}\[\]+-]+

#Need to use this => then look it at it recursivly 
#Since you can have (dffdsf:dsfsdf): dfsf
#\w+\s*=\s*[\w\.(),\"'{}\[\]+-]+\s*\?
    