import re
from typeMain import * 
from process import *
from function import *
from channel import *
from utility import *
import graphviz

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

    def link_channels_set(self):
        pattern= r'(\w+)\s*=\s*(CHANNEL_\d+)'
        for match in re.finditer(pattern, self.string):
            #print(match.group(0),match.group(1), match.group(2))
            c= self.get_channel(match.group(2))
            c.set_gives([match.group(1), 'P'])
            c.set_full_string(match.group(1)+' = '+c.get_string())
            self.string= self.string.replace(match.group(0), match.group(2), 1)
        #The case (var1, var2) or (var1, var2, ..., varX)
        pattern= r'\((\s*\w+\s*,(\s*\w+\s*,)*\s*\w+\s*)\)\s*=\s*(CHANNEL_\d+)'
        for match in re.finditer(pattern, self.string):
            c= self.get_channel(match.group(3))
            temp=match.group(1)
            temp= temp.split(',')
            for t in temp:
                t= t.strip()
                c.set_gives([t, 'P'])
            c.set_full_string(match.group(1)+' = '+c.get_string())
            self.string= self.string.replace(match.group(0), match.group(3), 1)


    #Method pas parfait 
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
        #print(str(index))
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
        self.link_channels_set()

    
        #=================================================================
        #FIFTH PART: INITIALISE THE CHANNELS
        #=================================================================
        #TODO: when we initialise it over-writes the thing just above 
        """for c in self.channels:
            c.initialise_channel()"""
            

        #return string, channels

    def check_attributions(self):
        #=================================================================
        #FOURTH PART: LINK THE TYPES CHANNEL THAT ARE DEFINED AS ... = ... => affectation
        #=================================================================
        index= len(self.channels)
        pattern= r'\w+ *= *\w+'
        all, dots=[], []
        for match in re.finditer(pattern, self.string):
            all.append(match.group(0))
        pattern= r'\.\w+ *= *\w+'
        #print('all', all)
        for match in re.finditer(pattern, self.string):
            dots.append(match.group(0).replace('.', ''))
        #print('dots', dots)
        tab= list(set(all) - set(dots))
        #print('tab', tab)
        for c in tab:
            name= 'CHANNEL_'+str(index)
            code= c
            temp_channel= Channel(name, code)
            temp_channel.not_normal()
            self.channels.append(temp_channel)
            index+=1
        for c in self.channels:
            #print(c.get_id(), c.get_string())
            self.string= self.string.replace(c.get_string(), c.get_id(), 1)

    def print_channels(self):
        for c in self.channels:
            print(c.get_id(), 'string :', c.get_full_string())
            print(c.get_id(), 'origin :',  c.get_origin())
            print(c.get_id(), 'gives  :',  c.get_gives())

    def save_channels(self, address= "/home/george/Bureau/TER/", name='channels'):
        myText = open(address+name+'.nf','w')
        for c in self.channels:
            #myText.write(str(c.get_gives())+' <- '+c.get_string()+'\n\n')
            myText.write(c.get_id()+ ' string : '+c.get_full_string()+'\n')
            myText.write(c.get_id()+' origin : '+  str(c.get_origin())+'\n')
            myText.write(c.get_id() +' gives  : '+  str(c.get_gives())+'\n\n\n')


        myText.close()
    
    def initialise_channels(self):
        for c in self.channels:
            c.initialise_channel()





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
    #METHODS to manipulate ifs
    #===========================================
    #TODO add case ?:
    def clean_up_if_double_dots_question(self):
        pattern= r'([^\=\n]+)\s*=\s*([^\?\n]+)\s*\?\s*([^\:\n]+)\s*\:\s*([^\n]+)'
        for match in re.finditer(pattern, self.string):
            #print(match.group(0))
            variable = match.group(1)
            condition = match.group(2)
            condition_true = match.group(3)
            condition_false = match.group(4)
            new_string="if("+condition+") { \n"+variable+" = "+condition_true+"\n } else { \n"+variable+" = "+condition_false+"\n } "
            self.string= self.string.replace(match.group(0), new_string)
        #Update the sets in the channels
        self.link_channels_set()
    
    def clean_up_if_one_line(self):
        self.string= add_curly(add_spaces(self.string))
    
    def format_ifs(self):
        self.string= format_conditions(self.string)

    def create_channels_links(self, dot, name):
        dot.node(name, '', color= '1', shape='doublecircle')
    
    def create_edge(self, dot, l1, l2, la):
        dot.edge(l1, l2, constraint='true', label=la)
        


    #===========================================
    #METHODS STRUCTURE
    #===========================================
    def get_structure(self, address= "/home/george/Bureau/TER/"):
        dot = graphviz.Digraph(filename='structure_worklow', format='png', comment='structure'\
                                 , node_attr={'colorscheme': 'pastel19', 'style': 'filled'})
        #ADD THE PREOCESSES
        for p in self.processes:
            #p.printName()
            input, output= p.extractAll()
            #print('input :', input)
            #print('output :', output)
            dot.node(p.getName(), p.getName(), color= '2', shape='box')
        
        #ADD THE CHANNELS (LINKS)
        added_link= True
        temp_channels, temp_processes= self.channels.copy(), self.processes.copy()
        links_added=[]
        channels_added=[]
        while(added_link):
            added_link = False

            #===============================================================
            #Case p.output -> p.input
            #===============================================================
            for p1 in temp_processes:
                    input_p1, output_p1= p.extractAll()
                    for p2 in temp_processes:
                        if(p1!=p2):
                            input_p2, output_p2= p.extractAll()
                            if(output_p1== input_p2):
                                reference='{}:{} -> {}:{}'.format(p1.getName(),output_p1 , p2.getName(), output_p2)
                                if(not check_containing(reference, links_added)):
                                    added_link = True
                                    links_added.append(reference)
                                    #dot.edge(p1.getName(), p2.getName(), constraint='true', label=output_p1)
                                    self.create_edge(dot, p1.getName(), p2.getName(), output_p1)



            for c1 in temp_channels:
                c1_gives= c1.get_gives()
                c1_origin= c1.get_origin()
                #Processes
                for p in temp_processes:
                    input, output= p.extractAll()
                    #===============================================================
                    #Case c1_gives -> p.input
                    #TODO right now we're not looking at the type or checking at least -> see HERE1
                    #===============================================================
                    for c1_gives_for in c1_gives:
                        c_name, type_c=  c1_gives_for[0], c1_gives_for[1]
                        for input_for in input:
                            id_input, input_name=  input_for[0], input_for[1]
                            #print(c_name, input_name)
                            #TODO HERE1
                            if(type_c=='P'):
                                if(c_name == input_name):
                                    reference='{}:{} -> {}:{}'.format(c1.get_id(), c_name, p.getName(), input_name)
                                    if(not check_containing(reference, links_added)):
                                        if(not check_containing(c1.get_id(), channels_added)):
                                            #TODO Find what to put in the channel to show
                                            self.create_channels_links(dot, c1.get_id())
                                            channels_added.append(c1.get_id())
                                        added_link = True
                                        links_added.append(reference)
                                        #dot.edge(c1.get_id(), p.getName(), constraint='true', label=c_name)
                                        self.create_edge(dot, c1.get_id(), p.getName(), c_name)
                    #===============================================================
                    #Case p.output -> c1_origin
                    #===============================================================
                    for output_for in output:
                        id_output, output_name= output_for[0], output_for[1]
                        for c1_origin_for in c1_origin:
                            c_name, type_c=  c1_origin_for[0], c1_origin_for[1]
                            if(type_c=='P'):
                                if(c_name == output_name):
                                    reference='{}:{} -> {}:{}'.format(p.getName(), output_name, c1.get_id(), c_name)
                                    if(not check_containing(reference, links_added)):
                                        if(not check_containing(c1.get_id(), channels_added)):
                                            #TODO Find what to put in the channel to show
                                            self.create_channels_links(dot, c1.get_id())
                                            channels_added.append(c1.get_id())
                                        added_link = True
                                        links_added.append(reference)
                                        #print(reference)
                                        #dot.edge(p.getName(),c1.get_id(), constraint='true', label=c_name)
                                        self.create_edge(dot, p.getName(), c1.get_id(), c_name)

                #===============================================================
                #Case c1_gives -> c2_origin
                #===============================================================
                for c1_gives_for in c1_gives:
                    c1_name, type_c1=  c1_gives_for[0], c1_gives_for[1]
                    if(type_c1=='P'):
                        for c2 in temp_channels:
                            if(c1!=c2):
                                c2_gives= c2.get_gives()
                                c2_origin= c2.get_origin()
                                #Obsiously if they're diffrent
                                for c2_origin_for in c2_origin:
                                    c2_name, type_c2=  c2_origin_for[0], c2_origin_for[1]
                                    if(type_c2=='P'):
                                        if(c2_name == c1_name):
                                            reference='{}:{} -> {}:{}'.format(c1.get_id(), c1_name, c2.get_id(), c2_name)
                                            if(not check_containing(reference, links_added)):
                                                if(not check_containing(c1.get_id(), channels_added)):
                                                    #TODO Find what to put in the channel to show
                                                    self.create_channels_links(dot, c1.get_id())
                                                    channels_added.append(c1.get_id())
                                                if(not check_containing(c2.get_id(), channels_added)):
                                                    #TODO Find what to put in the channel to show
                                                    self.create_channels_links(dot, c2.get_id())
                                                    channels_added.append(c2.get_id())
                                                added_link = True
                                                links_added.append(reference)
                                                #print(reference)
                                                #dot.edge(c1.get_id(),c2.get_id(), constraint='true', label=c1_name)
                                                self.create_edge(dot, c1.get_id(), c2.get_id(), c1_name)

        dot.render(directory=address)
        dot.save(directory=address)

    def get_structure_2(self, address= "/home/george/Bureau/TER/"):
        dot = graphviz.Digraph(filename='structure_worklow_2', format='png', comment='structure'\
                                 , node_attr={'colorscheme': 'pastel19', 'style': 'filled'})
        #[0] -> the pointer and [1] -> of what (either process or channel)
        tab_origin, tab_gives= [], []
        #ADD THE PREOCESSES
        for p in self.processes:
            #p.printName()
            input, output= p.extractAll()
            for i in input:
                id, name= i[0], i[1]
                tab_origin.append([name, p.getName()])
            for o in output:
                id, name= o[0], o[1]
                tab_gives.append([name, p.getName()])
            #print('input :', input)
            #print('output :', output)
            dot.node(p.getName(), p.getName(), color= '2', shape='box')

        links_added=[]
        temp_channels, temp_processes= self.channels.copy(), self.processes.copy()
        #===============================================================
        #Case p.output -> p.input
        #===============================================================
        #For earch process
        for p1 in temp_processes:
            #Get the inputs and outputs
            input_p1, output_p1= p1.extractAll()
            #For the other processes
            for p2 in temp_processes:
                #Check it's not the same process
                if(p1!=p2):
                    #Get the inputs and outputs
                    input_p2, output_p2= p2.extractAll()
                    #For each inputs and outputs for both processes
                    for output_p1_for_full in output_p1:
                        output_p1_for_id, output_p1_for= output_p1_for_full[0], output_p1_for_full[1]
                        for input_p2_for_full in input_p2:
                            input_p2_for_id, input_p2_for= input_p2_for_full[0], input_p2_for_full[1]
                            #check if the link matches
                            if(output_p1_for== input_p2_for):
                                reference='{}:{} -> {}:{}'.format(p1.getName(),output_p1_for , p2.getName(), input_p2_for)
                                #Check that we've not already added it to the graph
                                if(not check_containing(reference, links_added)):
                                    #Adding it to the graph
                                    links_added.append(reference)
                                    #dot.edge(p1.getName(), p2.getName(), constraint='true', label=output_p1)
                                    self.create_edge(dot, p1.getName(), p2.getName(), output_p1_for)
        
        #The next step is starting from the inputs and outputs from the different processes and linking the rest of the structure from that
        added_link= True
        channels_added=[]
        index=1
        while(added_link):
            #print('here')
            added_link = False
            new_channels_added=[]
            #===========================================
            #===========================================
            #From the origin tab
            #===========================================
            #===========================================
            for origin in tab_origin:
                origin_name, name_thing= origin[0], origin[1]
                for c in temp_channels:
                    c_gives= c.get_gives()
                    for c_gives_for in c_gives:
                        c_name, type_c=  c_gives_for[0], c_gives_for[1]
                        if(type_c=='P'):
                            if(c_name== origin_name):
                                reference='{}:{} -> {}:{}'.format(c.get_id(), c_name , name_thing, origin_name)
                                if(not check_containing(reference, links_added)):
                                    links_added.append(reference)
                                    if(not check_containing(c.get_id(), channels_added)):
                                        #TODO Find what to put in the channel to show
                                        self.create_channels_links(dot, c.get_id())
                                        channels_added.append(c.get_id())
                                        new_channels_added.append(c)
                                    self.create_edge(dot, c.get_id(), name_thing, c_name)
                                    added_link= True
                
            for c in new_channels_added:
                c_origin, c_gives= c.get_origin(), c.get_gives()
                for o in c_origin:
                    tab_origin.append([o, c.get_id()])
                for g in c_gives:
                    tab_gives.append([g, c.get_id()])    

            #===========================================
            #===========================================
            #From the gives tab
            #===========================================
            #===========================================
            new_channels_added=[]
            for gives in tab_gives:
                gives_name, name_thing= gives[0], gives[1]
                for c in temp_channels:
                    c_origin= c.get_origin()
                    for c_origin_for in c_origin:
                        c_name, type_c=  c_origin_for[0], c_origin_for[1]
                        if(type_c=='P'):
                            if(c_name== gives_name):
                                reference='{}:{} -> {}:{}'.format(name_thing, gives_name, c.get_id(), c_name)
                                if(not check_containing(reference, links_added)):
                                    links_added.append(reference)
                                    if(not check_containing(c.get_id(), channels_added)):
                                        #TODO Find what to put in the channel to show
                                        self.create_channels_links(dot, c.get_id())
                                        channels_added.append(c.get_id())
                                        new_channels_added.append(c)
                                    self.create_edge(dot,name_thing, c.get_id(),c_name)
                                    added_link= True
                
            for c in new_channels_added:
                c_origin, c_gives= c.get_origin(), c.get_gives()
                for o in c_origin:
                    tab_origin.append([o, c.get_id()])
                for g in c_gives:
                    tab_gives.append([g, c.get_id()])
        
        
        dot.render(directory=address)
        dot.save(directory=address)

    #TODO:
    #   - Need to add support => not just for pointers but for file and other types
    #   - Right documentations for the method
    #   - Check the difference between 2 and 3 => don't understand why it works but it does so hey ho
    #Method that constructs the structure of the workflow thanks to the list of channels and processes
    def get_structure_3(self, address= "/home/george/Bureau/TER/"):
        #Start by defining the graphviz diagram
        dot = graphviz.Digraph(filename='structure_worklow_3', format='png', comment='structure'\
                                 , node_attr={'colorscheme': 'pastel19', 'style': 'filled'})
        #Defining 2 lists: tab_origin and tab_gives
        #These 2 lists allow us to get the structure since we start from the processes
        #and follow the 'route' which is drawn for us
        #tab_origin contains all the elements c such as x -> c for every x 
        #tab_gives contains all the elements c such as c -> x for every x 
        #[0] -> the pointer and [1] -> of what (either process or channel)
        tab_origin, tab_gives= [], []
        #Start by adding all the inputs and outputs of the processes 
        #to the different lists => since there is no (~or very little) false positives
        for p in self.processes:
            input, output= p.extractAll()
            for i in input:
                id, name= i[0], i[1]
                tab_origin.append([name, p.getName()])
            for o in output:
                id, name= o[0], o[1]
                tab_gives.append([name, p.getName()])
            #Adding the processes to the diagram/ network
            dot.node(p.getName(), p.getName(), color= '2', shape='box')
        #Defining the list links_added which allows us to check if we have already added 
        #a link to the network => it is just to avoid redundancies 
        links_added=[]
        temp_channels, temp_processes= self.channels.copy(), self.processes.copy()
        
        #print('Gives: ', c.get_gives())
        #print('Origin: ', c.get_origin())
        #print(temp_channels[0].get_gives(), '\n')
        #===============================================================
        #Case p.output -> p.input
        #===============================================================
        #For earch process
        for p1 in temp_processes:
            #Get the inputs and outputs
            input_p1, output_p1= p1.extractAll()
            #For the other processes
            for p2 in temp_processes:
                #Check it's not the same process
                if(p1!=p2):
                    #Get the inputs and outputs
                    input_p2, output_p2= p2.extractAll()
                    #For each inputs and outputs for both processes
                    for output_p1_for_full in output_p1:
                        output_p1_for_id, output_p1_for= output_p1_for_full[0], output_p1_for_full[1]
                        for input_p2_for_full in input_p2:
                            input_p2_for_id, input_p2_for= input_p2_for_full[0], input_p2_for_full[1]
                            #check if the link matches
                            if(output_p1_for== input_p2_for):
                                reference='{}:{} -> {}:{}'.format(p1.getName(),output_p1_for , p2.getName(), input_p2_for)
                                #Check that we've not already added it to the graph
                                if(not check_containing(reference, links_added)):
                                    #Adding it to the graph
                                    links_added.append(reference)
                                    #dot.edge(p1.getName(), p2.getName(), constraint='true', label=output_p1)
                                    self.create_edge(dot, p1.getName(), p2.getName(), output_p1_for)
        
        #The next step is starting from the inputs and outputs from the different processes and linking the rest of the structure from that
        added_link= True
        channels_added=[]
        index=1
        while(added_link):
            #print('here')
            #print(tab_origin, '\n')
            added_link = False
            new_channels_added=[]
            #===========================================
            #===========================================
            #From the origin tab
            #===========================================
            #===========================================
            for origin in tab_origin:
                origin_name, name_thing= origin[0], origin[1]
                for c in temp_channels:
                    c_gives= c.get_gives()
                    for c_gives_for in c_gives:
                        c_name, type_c=  c_gives_for[0], c_gives_for[1]
                        if(type_c=='P'):
                            if(c_name== origin_name):
                                reference='{}:{} -> {}:{}'.format(c.get_id(), c_name , name_thing, origin_name)
                                #print(reference)
                                if(not check_containing(reference, links_added)):
                                    links_added.append(reference)
                                    if(not check_containing(c.get_id(), channels_added)):
                                        #TODO Find what to put in the channel to show
                                        self.create_channels_links(dot, c.get_id())
                                        channels_added.append(c.get_id())
                                        new_channels_added.append(c)
                                    self.create_edge(dot, c.get_id(), name_thing, c_name)
                                    added_link= True
                
                #Add the same for the processes
                for p in temp_processes:
                    if(p.getName()!=name_thing):
                        #Get the inputs and outputs
                        input_p, output_p= p.extractAll()
                        #For each inputs and outputs for both processes
                        for output_p_full in output_p:
                            output_p_id, output_p_name= output_p_full[0], output_p_full[1]
                            if(output_p_name== origin_name):
                                reference='{}:{} -> {}:{}'.format(p.getName(),output_p_name , name_thing, origin_name)
                                #Check that we've not already added it to the graph
                                if(not check_containing(reference, links_added)):
                                    #Adding it to the graph
                                    links_added.append(reference)
                                    #dot.edge(p1.getName(), p2.getName(), constraint='true', label=output_p1)
                                    self.create_edge(dot, p.getName(), name_thing, output_p_name)
                                    added_link= True
                
            for c in new_channels_added:
                c_origin, c_gives= c.get_origin(), c.get_gives()
                for o in c_origin:
                    if(o[1]=='P'):
                        tab_origin.append([o[0], c.get_id()])
                for g in c_gives:
                    if(g[1]=='P'):
                        tab_gives.append([g[0], c.get_id()])    

            #===========================================
            #===========================================
            #From the gives tab
            #===========================================
            #===========================================
            new_channels_added=[]
            new_processes_added=[]
            for gives in tab_gives:
                gives_name, name_thing= gives[0], gives[1]
                for c in temp_channels:
                    c_origin= c.get_origin()
                    for c_origin_for in c_origin:
                        c_name, type_c=  c_origin_for[0], c_origin_for[1]
                        if(type_c=='P'):
                            if(c_name== gives_name):
                                reference='{}:{} -> {}:{}'.format(name_thing, gives_name, c.get_id(), c_name)
                                if(not check_containing(reference, links_added)):
                                    links_added.append(reference)
                                    if(not check_containing(c.get_id(), channels_added)):
                                        #TODO Find what to put in the channel to show
                                        self.create_channels_links(dot, c.get_id())
                                        channels_added.append(c.get_id())
                                        new_channels_added.append(c)
                                    self.create_edge(dot,name_thing, c.get_id(),c_name)
                                    added_link= True

                #Add the same for the processes
                for p in temp_processes:
                    
                    if(p.getName()!=name_thing):
                        
                        #Get the inputs and outputs
                        input_p, output_p= p.extractAll()
                        #For each inputs and outputs for both processes
                        for input_p_full in input_p:
                            input_p_id, input_p_name= input_p_full[0], input_p_full[1]
                            if(input_p_name== gives_name):
                                reference='{}:{} -> {}:{}'.format(name_thing, gives_name, p.getName(),input_p_name )
                                #Check that we've not already added it to the graph
                                if(not check_containing(reference, links_added)):
                                    #Adding it to the graph
                                    links_added.append(reference)
                                    #dot.edge(p1.getName(), p2.getName(), constraint='true', label=output_p1)
                                    self.create_edge(dot, name_thing, p.getName(),input_p_name)
                                    added_link= True
                
            for c in new_channels_added:
                c_origin, c_gives= c.get_origin(), c.get_gives()
                for o in c_origin:
                    if(o[1]=='P'):
                        tab_origin.append([o[0], c.get_id()])
                for g in c_gives:
                    if(g[1]=='P'):
                        tab_gives.append([g[0], c.get_id()])   
        
        
        dot.render(directory=address)
        dot.save(directory=address)
        

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

        self.clean_up_if_double_dots_question()
        self.clean_up_if_one_line()
        
        self.temp_workflow_onComplete()

        self.format_ifs()

        self.check_attributions()

        self.initialise_channels()
        #self.print_channels()
        

def tests():
    m= TypeMainDSL1("/home/george/Bureau/TER/Prototypes/Nextflow_tests_for_channels/test.nf")
    m.initialise()
    m.save_file()

def test_structure(adresse= "/home/george/Bureau/TER/Workflow_Database/Tests/Test2/main.nf"):
    m= TypeMainDSL1(adresse)
    m.initialise()
    #m.get_structure()
    m.get_structure()
    m.get_structure_2()
    m.get_structure_3()
#=================
#IF USED AS A MAIN
#=================
if __name__ == "__main__":
    #print("I shoudn't be executed as a main")
    #See Line 344
    """m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/samba-master/main.nf")
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/eager-master/main.nf")
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/hic-master/main.nf")
    #Still need to look into sarek
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/sarek-master/main.nf")
    #Seen that there is a bug with condition
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/smrnaseq-master/main.nf")
    #Major problem here
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/metaboigniter-master/main.nf")
    m.initialise()
    m.get_structure()
    m.get_structure_3()
    m.get_structure_2()
    #m.print_name_processes()

    m.save_file()
    m.save_channels()"""
    test_structure()
    #tests()
    #m.print_processes()

    #m.print_name_functions()
    #print(m.get_nb_functions())
    #m.print_file()


#TODO List
# - And to link everything together after
# - Remove comments is still not perfect=> see metaboigniter
# - workflow.onError
# - CONDITIONS!!!!
# - I don't like the way i've defined the reconstruction of the structure => it does everythong and doesn't start at processes and finds the route from there => doesn't know if this makes sense but you understand ;)
    