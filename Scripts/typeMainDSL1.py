from distutils.command.install_egg_info import to_filename
import re
from typeMain import * 
from process import *
from function import *
from channel import *
from utility import *
import graphviz


class TypeMainDSL1(TypeMain):
    def __init__(self, address, root):
        super().__init__(address, root)
        self.processes=[]
        self.functions=[]
        self.channels=[]
        self.added_operators= []
        #TODO
        #This attribute is temporary
        self.onComplete=[]
        self.onError= []
        self.can_analyse=True
        


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
            #print(work[end])
            if(work[end] == "{"):
                count_curly += 1
            elif(work[end] == "}"):
                count_curly -= 1
            end += 1
        return end

    def right_nb_curly(self):
        if(self.string.count('{')==self.string.count('}')):
            return True
        return False




















    #===========================================
    #METHODS FOR MANIPULATING PROCESSES
    #===========================================

    #Finds and adds the processes to the list of processes
    #Plus analyse the processes 
    def find_processes(self):
        pattern=  r'([^\w]?process\s+\w+\s*{)'
        for match in re.finditer(pattern, self.string):
            start= match.span()[0]
            end= self.extract_curly(match.span()[1])
            process= Process(self.string[start:end])
            process.extractProcess(False)
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
    
    def save_processes(self, address= "/home/george/Bureau/TER/", name='processes'):
        myText = open(address+name+'.nf','w')
        for p in self.processes:
            #myText.write(str(c.get_gives())+' <- '+c.get_string()+'\n\n')
            myText.write('Name : '+p.getName()+'\n')
            input, output, emit= p.extractAll()
            myText.write('Inputs : '+  str(input)+'\n')
            myText.write('Outputs : '+  str(output)+'\n')
            myText.write('Emits : '+  str(emit)+'\n\n\n')

    
    













    #===========================================
    #METHODS FOR MANIPULATING CHANNELS
    #===========================================
    
    #Method that extratcs the channel => finds the end of the channel
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
    def extract_added_operators(self):
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
        to_change=[]
        for match in re.finditer(pattern, self.string):
            #print(match.group(0),match.group(1), match.group(2))
            c= self.get_channel(match.group(2))
            c.set_gives([match.group(1), 'P'])
            c.set_full_string(match.group(1)+' = '+c.get_string())
            #self.string= self.string.replace(match.group(0), match.group(2), 1)
            to_change.append([match.group(0), match.group(2)])
        for c in to_change:
            self.string= self.string.replace(c[0], c[1], 1)

        #The case (var1, var2) or (var1, var2, ..., varX)
        pattern= r'\((\s*\w+\s*,(\s*\w+\s*,)*\s*\w+\s*)\)\s*=\s*(CHANNEL_\d+)'
        to_change=[]
        for match in re.finditer(pattern, self.string):
            c= self.get_channel(match.group(3))
            temp=match.group(1)
            temp= temp.split(',')
            for t in temp:
                t= t.strip()
                c.set_gives([t, 'P'])
            c.set_full_string(match.group(1)+' = '+c.get_string())
            #self.string= self.string.replace(match.group(0), match.group(3), 1)
            to_change.append([match.group(0), match.group(3)])
        for c in to_change:
            self.string= self.string.replace(c[0], c[1], 1)

    def get_added_operators(self):
        return self.added_operators

    def initialise_channels(self):
        for c in self.channels:
            c.initialise_channel()

    def get_all_defined_channels(self):
        tab=[]
        for c in self.channels:
            origin = c.get_origin()
            gives = c.get_gives()
            for o in origin:
                if(o[1]=='P'):
                    tab.append(o[0])
  
            for g in gives:
                if(g[1]=='P'):
                    tab.append(g[0])
        return list(set(tab))

    def get_inputs_and_outputs_processe(self):
        tab=[]

        for p in self.processes:
            #print(p.getAll())
            input, output, emit= p.extractAll()
            for i in input:
                tab.append(i[1])
            for o in output:
                tab.append(o[1])
        return list(set(tab))

    def extract_analyse_channels(self):
        #=================================================================
        #PART ZERO: BEFORE WE START WE NEED TO EXTRACT THE ADDED OPERATORS CREATED WITH BRANCH OR MULTIMAP
        #=================================================================
        ope= self.extract_added_operators()
        added= '|'.join(ope)
        if added != '':
            added='|'+added
        #print(added)
        #TODO I think we do this to see make the recognition of channels easier later on
        for o in ope:
            pattern=r'\.\s*('+o+')\s*\.'
            for match in re.finditer(pattern, self.string):
                word=match.group(0)
                self.string= self.string.replace(word, '.{}().'.format(o), 1)
                #print('.{}().'.format(o))
        self.added_operators= ope

        #In the following we replace the channel format in a weird way, in a while loop 
        # and a for with a brak => basically everytime we see a channel that matches the pattern
        # it is replaced imedialtly => so we have to reload the new positions in the string that's way there 
        # is the break => we do this to avoid weird bugs due to the map operator => basically you can use 
        # function in groovy for example with the same syntaxe as the channel operators => so it was doing
        # this weird thing where it was recognising a channel in a channel and it created a loop in the structure
        # Writtig the code in this way avoids that problem by replacing the channel as soon as it sees it
        #=================================================================
        #FIRST PART: WE EXTRACT THE ONES WITH THE WORD CHANNEL 
        #=================================================================
        pattern= r'[^\w]((C|c)hannel\s*\.)'
        index=1
        changed= True
        while(changed):
            changed=False
            for match in re.finditer(pattern, self.string):
                start= match.span(1)[0]
                #print(match.span(1))
                end= self.get_end_channel(start)
                code= self.string[start:end]
                #print(code)
                #print(code)
                name= 'CHANNEL_'+str(index)
                self.channels.append(Channel(name, code))
                index+=1

                changed=True
                self.string= self.string.replace(code, name, 1)
                break

        #=================================================================
        #SECOND PART: WE EXTRACT THE OTHER ONES 
        #=================================================================
        operations= 'distinct|filter|first|last|randomSample|take|unique|until|buffer|collate|collect|flatten|flatMap|groupBy|groupTuple|map|reduce|toList|toSortedList|transpose|splitCsv|splitFasta|splitFastq||splitText|cross|collectFile|combine|concat|join|merge|mix|phase|spread|branch|choice|multiMap|into|separate|tap|count|countBy|min|max|sum|toInteger|close|dump|ifEmpty|print|println|set|view|create|empty|from|fromPath|fromFilePairs|fromSRA|of|value|watchPath|subscribe'+added
        pattern= r'(\w+)\s*\.\s*('+operations+')\s*({|\()'
        tab=[]
        changed= True
        while(changed):
            changed=False
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

                    changed=True
                    self.string= self.string.replace(code, name, 1)
                    break

        #=================================================================
        #THIRD PART: LINK THE TYPES CHANNEL THAT ARE DEFINED AS ... = CHANNEL_ID
        #=================================================================
        self.link_channels_set()

        self.initialise_channels()


        #=================================================================
        #FOURTH PART: LINK THE TYPES CHANNEL THAT ARE DEFINED AS ... = ...
        #=================================================================
        #Get all the occurence of word = word
        pattern= r'\w+ *= *\w+'
        all, dots=[], []
        for match in re.finditer(pattern, self.string):
            all.append(match.group(0))
        #Get all the occurence of .word = word then replace the '.' with nothings
        pattern= r'\.\w+ *= *\w+'
        for match in re.finditer(pattern, self.string):
            dots.append(match.group(0).replace('.', ''))
        #Removing the occurences of .word = word
        tab= list(set(all) - set(dots))

        #Organising tab in a linear order:
        order=[]
        for t in tab:
             order.append(self.string.index(t))
        order_sorted= sorted(range(len(order)), key=lambda k: order[k])

        #print(tab)
        tab_all_definied_channels= self.get_all_defined_channels()
        tab_all_definied_inputs_outputs= self.get_inputs_and_outputs_processe()
        #print(tab_all_definied_channels)
        for i in order_sorted:
            c= tab[i]
            pattern= r'(\w+) *= *(\w+)'
            left, right='', ''
            for match in re.finditer(pattern, c):
                right= match.group(2)
                left= match.group(1)
            if (is_in(tab_all_definied_channels, right) or is_in(tab_all_definied_inputs_outputs, right)):
                #print('her')
                name= 'CHANNEL_'+str(index)
                code= c
                temp_channel= Channel(name, code)
                temp_channel.not_normal()
                self.channels.append(temp_channel)
                index+=1
                tab_all_definied_channels.append(left)
        for c in self.channels:
            self.string= self.string.replace(c.get_string(), c.get_id(), 1)

        self.initialise_channels()


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

    def get_channels_formated(self):
        temp=""
        for c in self.channels:
            temp+=(c.get_id()+ ' string : '+c.get_full_string()+'\n')
            temp+=(c.get_id()+' origin : '+  str(c.get_origin())+'\n')
            temp+=(c.get_id() +' gives  : '+  str(c.get_gives())+'\n\n\n')
        return temp

    
    









    #===========================================
    #METHODS FOR MANIPULATING FUNCTIONS
    #===========================================

    #Finds and adds the functions to the list of functions
    def find_functions(self):
        pattern= r'def +\w+ *\([^\)]*\)\s*{'
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

    #Returns a list of the name of the functions
    def get_name_functions(self):
        tab=[]
        for f in self.functions:
            tab.append(f.get_name())
        return tab

    #Checks if a given name is a function
    def check_name_is_function(self, name):
        list= self.get_name_functions()
        if(list.count(name)==0):
            return False
        return True


    def clean_function(self):
        self.find_functions()
        self.format_functions()
    









    #For know we are just gonna put the string in an attribute (string) and not analyse it YET
    #My intuition right now is to create a subworkflow with the workflow.onComplete in it
    #Or maybe create a new class 
    #===========================================
    #METHODS FOR workflow.onComplete
    #===========================================
    def workflow_onComplete(self):
        pattern= r'(workflow.onComplete\s*{)'
        for match in re.finditer(pattern, self.string):
            #Finding the pattern
            start= match.span()[0]
            print(self.string[start:match.span()[1]])
            end= self.extract_curly(match.span()[1])
            self.onComplete.append( self.string[start:end])
            #Replacing the declaration by a marker
            self.string= self.string.replace(self.string[start:end], 'WORKFLOW ON_COMPLETE', 1)













    #===========================================
    #METHODS FOR workflow.onError
    #===========================================
    def workflow_onError(self):
        pattern= r'(workflow.onError\s*{)'

        for match in re.finditer(pattern, self.string):
            #This is just to test the fact that there isn't over one declaration
            #Finding the pattern
            start= match.span()[0]
            end= self.extract_curly(match.span()[1])
            self.onError.append( self.string[start:end])
            #Replacing the declaration by a marker
            self.string= self.string.replace(self.string[start:end], 'WORKFLOW ON_ERROR', 1)
            









    #===========================================
    #METHODS to manipulate ifs
    #===========================================
    
    def clean_up_if_double_dots_question_2(self):
        pattern= r'([^\=\n]+)\s*=\s*([^\?\n]+)\s*\?([^\n]+)'
        to_be_added=[]
        for match in re.finditer(pattern, self.string):
            variable = match.group(1)
            condition = match.group(2)

            #We have to identify the 2 different case by 'hand' because there can be a ':' in a paranthesis for example
            #In that case we can't use a regex pattern
            start= match.span(3)[0]
            end=match.span(3)[1]
            i=start
            para_count, curly_count=0, 0
            s= self.string
            condition_true, condition_false= '', ''
            while(i<end):
                if(s[i]=='('):
                    para_count+=1
                elif(s[i]==')'):
                    para_count-=1
                elif(s[i]=='{'):
                    curly_count+=1
                elif(s[i]=='}'):
                    curly_count-=1

                elif(para_count==0 and curly_count ==0 and s[i]==':'):
                    condition_true= s[start:i]
                    condition_false= s[i+1:end]
                    break
                i+=1
        
            new_string="if ("+condition+") { \n"+variable+" = "+condition_true+"\n } else { \n"+variable+" = "+condition_false+"\n } "
            to_be_added.append([match.group(0), new_string])
        for a in to_be_added:
            self.string= self.string.replace(a[0], a[1])
        #Update the sets in the channels
        #self.link_channels_set()


    def clean_up_if_one_line(self):
        #self.string= add_curly(add_spaces(self.string))
        self.string= add_spaces(add_curly(self.string))
    
    def format_ifs(self):
        self.string= format_conditions(self.string)

            








    #===========================================
    #METHODS STRUCTURE
    #===========================================
    
    def create_edge(self, dot, l1, l2, la):
        dot.edge(l1, l2, constraint='true', label='')

    def create_node_type(self, dot, id, name, type):
        #id = 'CHANNEL_\d+' 
        name=id[8:]
        if(type=='A'):
            dot.node(id, name, color= '4', shape='doublecircle')
        elif(type=='V'):
            dot.node(id, name, color= '3', shape='doublecircle')
        elif(type=='S'):
            dot.node(id, name, color= '5', shape='doublecircle')
        elif(type=='P'):
            dot.node(id, name, color= '1', shape='doublecircle')
        elif(type=='F'):
            dot.node(id, name, color= '6', shape='doublecircle')

    def get_structure_4(self,name='structure_worklow_4',  address= "/home/george/Bureau/TER/"):
        if(self.can_analyse):
            #nb_links correspond aux nombre de lien de flux de données
            nb_process, nb_links= 0, 0
            #Start by defining the graphviz diagram
            dot = graphviz.Digraph(filename=name, format='png', comment='structure'\
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
                #print(p.getAll())
                input, output, emit= p.extractAll()
                for i in input:
                    id, name= i[0], i[1]
                    tab_origin.append([name, p.getName()])
                for o in output:
                    id, name= o[0], o[1]
                    tab_gives.append([name, p.getName()])
                #Adding the processes to the diagram/ network
                dot.node(p.getName(), p.getName(), color= '2', shape='box')
                nb_process +=1
            #Defining the list links_added which allows us to check if we have already added 
            #a link to the network => it is just to avoid redundancies 
            links_added=[]
            
            #print('Gives: ', c.get_gives())
            #print('Origin: ', c.get_origin())
            #print(self.channels[0].get_gives(), '\n')
            #===============================================================
            #Case p.output -> p.input
            #===============================================================
            #For earch process
            for p1 in self.processes:
                
                #TEMPORARY
                """input_p1, output_p1, emit_p1= p1.extractAll()
                for i in input_p1:
                    input_id, input_for= i[0], i[1]
                    dot.edge(input_for, p1.getName(), constraint='true', label='')
                for o in output_p1:
                    output_id, output_for= o[0], o[1]
                    dot.edge(p1.getName(), output_for, constraint='true', label='')"""
                #END TEMPORARY



                #Get the inputs and outputs
                input_p1, output_p1, emit_p1= p1.extractAll()
                #For the other processes
                for p2 in self.processes:
                    #Check it's not the same process
                    if(p1!=p2):
                        #Get the inputs and outputs
                        input_p2, output_p2, emit_p2= p2.extractAll()
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
                                        nb_links+=1
            
            #The next step is starting from the inputs and outputs from the different processes and linking the rest of the structure from that
            added_link= True
            channels_added=[]
            index=1
            while(added_link):
                #print('here')
                #print(tab_origin, '\n')
                added_link = False
                #===========================================
                #===========================================
                #From the origin tab
                #===========================================
                #===========================================
                new_channels_added=[]
                for origin in tab_origin:
                    origin_name, name_thing= origin[0], origin[1]
                    for c in self.channels:
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
                                            #self.create_channels_links(dot, c.get_id())
                                            types=[]
                                            i=0
                                            for c_origin in c.get_origin():
                                                c_origin_name, type_c_origin= c_origin[0], c_origin[1]
                                                types.append(type_c_origin)
                                            #print(types)
                                            if(len(list(set(types)))!=1):
                                                if(is_in(types, 'P') or list(set(types))== []):
                                                    t='P'
                                                else:
                                                    #TODO find better way than this 
                                                    t=types[0]
                                                    print(f'WARNING!!! : Multiple origin types for {c_name}')
                                                    print(f'The code is {c.get_string()}')
                                            else:
                                                t= list(set(types))[0]
                                                #if(self.check_name_is_function(c_origin[0])):
                                                    #Function
                                                    #t = 'F'
                                            self.create_node_type(dot, c.get_id(), c.get_string(), t)
                                            channels_added.append(c.get_id())
                                            new_channels_added.append(c)
                                        self.create_edge(dot, c.get_id(), name_thing, c_name)
                                        nb_links+=1
                                        added_link= True
                    
                    #Add the same for the processes
                    for p in self.processes:
                        if(p.getName()!=name_thing):
                            #Get the inputs and outputs
                            input_p, output_p, emit_p= p.extractAll()
                            #For each inputs and outputs for both processes
                            for output_p_full in output_p:
                                output_p_id, output_p_name= output_p_full[0], output_p_full[1]
                                if(output_p_name== origin_name):
                                    reference='{}:{} -> {}:{}'.format(p.getName(),output_p_name , name_thing, origin_name)
                                    #Check that we've not already added it to the graph
                                    if(not check_containing(reference, links_added)):
                                        print(reference)
                                        #Adding it to the graph
                                        links_added.append(reference)
                                        #dot.edge(p1.getName(), p2.getName(), constraint='true', label=output_p1)
                                        self.create_edge(dot, p.getName(), name_thing, output_p_name)
                                        nb_links+=1
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
                for gives in tab_gives:
                    gives_name, name_thing= gives[0], gives[1]
                    for c in self.channels:
                        c_origin= c.get_origin()
                        for c_origin_for in c_origin:
                            c_name, type_c=  c_origin_for[0], c_origin_for[1]
                            if(type_c=='P'):
                                if(c_name== gives_name):
                                    reference='{}:{} -> {}:{}'.format(name_thing, gives_name, c.get_id(), c_name)
                                    if(not check_containing(reference, links_added)):
                                        #print(reference)
                                        links_added.append(reference)
                                        if(not check_containing(c.get_id(), channels_added)):
                                            #TODO Find what to put in the channel to show
                                            #Forcement a pointeur
                                            self.create_node_type(dot, c.get_id(), c.get_string(), 'P')
                                            #self.create_channels_links(dot, c.get_id())
                                            channels_added.append(c.get_id())
                                            new_channels_added.append(c)
                                        self.create_edge(dot,name_thing, c.get_id(),c_name)
                                        nb_links+=1
                                        added_link= True

                    #Add the same for the processes
                    for p in self.processes:
                        
                        if(p.getName()!=name_thing):
                            
                            #Get the inputs and outputs
                            input_p, output_p, emit_p= p.extractAll()
                            #For each inputs and outputs for both processes
                            for input_p_full in input_p:
                                input_p_id, input_p_name= input_p_full[0], input_p_full[1]
                                if(input_p_name== gives_name):
                                    reference='{}:{} -> {}:{}'.format(name_thing, gives_name, p.getName(),input_p_name )
                                    #Check that we've not already added it to the graph
                                    if(not check_containing(reference, links_added)):
                                        #print(reference)
                                        #Adding it to the graph
                                        links_added.append(reference)
                                        #dot.edge(p1.getName(), p2.getName(), constraint='true', label=output_p1)
                                        self.create_edge(dot, name_thing, p.getName(),input_p_name)
                                        nb_links+=1
                                        added_link= True
                    
                for c in new_channels_added:
                    c_origin, c_gives= c.get_origin(), c.get_gives()
                    for o in c_origin:
                        if(o[1]=='P'):
                            tab_origin.append([o[0], c.get_id()])
                    for g in c_gives:
                        if(g[1]=='P'):
                            tab_gives.append([g[0], c.get_id()]) 
                                
            #print(address)
            dot.render(directory=address)
            dot.save(directory=address)
            return nb_process, nb_links
        else:
            return -1, -1













    #===========================================
    #GENERAL METHODS
    #===========================================

    #Saves the the worklfow string in a given address as a nextflow file
    def save_file(self, address= "/home/george/Bureau/TER/", name='formated_workflow'):
        myText = open(address+name+'.nf','w')
        myText.write(self.string)
        myText.close()

    #Supposing that remove comment works correctly
    #Initialise the basic stuff for a mainDSL1 type
    def initialise(self):
        #STEP1
        #In this mrthod just initialise the basic stuff (set string + remove comments)
        self.initialise_basic_main()

        if(self.right_nb_curly()):
            #STEP2
            #Finds and adds the proccesses to the list of processes + analysing them
            self.find_processes()
            self.format_processes()

            #STEP3
            #Finds and formats the function => In DSL1 functions are not important to the structure to we 'remove' (format) them
            #to simply the analysis of the workflow
            self.clean_function()

            #STEP4
            #We have to do this to update the channels which are in the double dots => otherwise the analyseur won't recongise them later on 
            self.clean_up_if_double_dots_question_2()


            #STEP5 
            #Find and analyse every channel and add them to the list of channels
            self.extract_analyse_channels()
            
            #self.clean_up_if_one_line()
            #print('self.clean_up_if_one_line()')
            
            
            #self.workflow_onComplete()
            #self.workflow_onError()
        else:
            print_in_red('WHEN A CURLY OPENS IT NEEDS TO BE CLOSED!')
            print_in_red("Didn't find the same number of open curlies then closing curlies")
            print_in_red("I CAN NOT ANALYSE THIS")
            self.can_analyse= False

        #self.format_ifs()
        #print('self.format_ifs()')
        
        
#===========================================
#TESTS
#===========================================

def tests():
    m= TypeMainDSL1("/home/george/Bureau/TER/test.nf")
    m.initialise()
    m.save_file()
    m.save_channels()
    m.save_processes()
    m.get_structure_4()

def test_structure(adresse= "/home/george/Bureau/TER/Workflow_Database/Tests/Test2/main.nf"):
    m= TypeMainDSL1(adresse)
    m.initialise()
    m.get_structure_4()







#=================
#IF USED AS A MAIN
#=================
if __name__ == "__main__":
    #print("I shoudn't be executed as a main")

    #These are the list of Workflows found in nf-core that we know are written in DSL1 => not difficult to identify 
         
    m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/samba-master/main.nf", "")
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/eager-master/main.nf", "")
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/hic-master/main.nf", "")
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/smrnaseq/main.nf", "")
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/sarek-master/main.nf", "")
    #m= TypeMainDSL1("/home/george/Bureau/TER/Workflow_Database/metaboigniter-master/main.nf", "")


    #YOU can delete this it's just to tests the channels
    #m= TypeMainDSL1("/home/george/Bureau/TER/Prototypes/extract_channels/temp.nf", "")

    
    #m= TypeMainDSL1("/home/george/Bureau/TER/test.nf", "")
    m.initialise()
    nb_processes, nb_links= m.get_structure_4()
    print(nb_processes, nb_links)
 
    m.save_file()
    m.save_channels()
    m.save_processes()


#TODO List
# - Remove comments is still not perfect=> see metaboigniter
# - workflow.onError
# - CONDITIONS!!!!
    
