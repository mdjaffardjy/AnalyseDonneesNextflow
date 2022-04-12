# Nextflow Analyzer
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022

import re
import graphviz

from .typeMain import * 
from .process import *
from .function import *
from .operation import *
from .utility import *


class TypeMainDSL1(TypeMain):
    def __init__(self, address):
        super().__init__(address)
        self.functions=[]
        self.operations=[]
        self.added_operators= []

        self.can_analyse=True
        self.name_workflow = ''
        
        self.nb_edges = 0
        self.nb_nodes_process = 0
        self.nb_nodes_operation = 0
        

    #==============================================
    #METHODS FOR MANIPULATING CHANNELS + OPERATIONS
    #==============================================

    #Method that extratcs the operation e.g Finds the end of the operation
    #Following the pattern that a operztion is finished when another doesn't concatenate with the end of it
    #Meaning when the next caracter isn't a '.' -> to add another operation at the end
    def get_end_operation(self, start, curly_count=0, parenthesis_count=0):
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
                    #TODO Find out why this is here
                    return index
                elif(self.string[index]=='\n' and get_next_element_caracter(self.string, index)[0]!='.'):
                    return index
            index+=1
        return index 


    def get_operation(self, id):
        for c in self.operations:
            if id== c.get_id():
                return c
        raise Exception('Opeartion not in list of operations')

    
    def extract_branches(self, start, end):
        string= self.string[start:end]
        tab=[]
        pattern= r'(\w+)\s*:'
        for match in re.finditer(pattern, string):
            tab.append(match.group(1))
        return tab

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

    def link_operations_set(self):
        pattern= r'(\w+)\s*=\s*(OPERATION_\d+)'
        to_change=[]
        for match in re.finditer(pattern, self.string):
            #print(match.group(0),match.group(1), match.group(2))
            c= self.get_operation(match.group(2))
            c.set_gives([match.group(1), 'P'])
            c.set_full_string(match.group(1)+' = '+c.get_string())
            #self.string= self.string.replace(match.group(0), match.group(2), 1)
            to_change.append([match.group(0), match.group(2)])
        for c in to_change:
            self.string= self.string.replace(c[0], c[1], 1)

        #The case (var1, var2) or (var1, var2, ..., varX)
        pattern= r'\((\s*\w+\s*,(\s*\w+\s*,)*\s*\w+\s*)\)\s*=\s*(OPERATION_\d+)'
        to_change=[]
        for match in re.finditer(pattern, self.string):
            c= self.get_operation(match.group(3))
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
    
    def find_problematic_operations(self):
        index=-1
        problematic_operations = []
        pattern = r'(\w+) *= *(\w+)'
        for c in self.operations:
            if c.get_full_string() != None :
                for match in re.finditer(pattern, c.get_full_string()):
                    if(match.group(1) == match.group(2)):
                        problematic_operations.append(match.group(1))
        
        def is_in(string, word):
            for i in range(0, len(string)-len(word)):
                if(string[i:i+len(word)]==word):
                    return True
            return False

        def containg(tab, word):
            for t in tab:
                if(t==word):
                    return True
            return False

        def remove_duplicates(list):
            ino=[]
            for l in list :
                if(not containg(ino, l)):
                    ino.append(l)
            return ino

        for ch in problematic_operations:
            operations_containing = []
            for c in self.operations:
                string=''
                if c.get_full_string() != None :
                    string = c.get_full_string()
                else:
                    string = c.get_string()
                if(is_in(string, ch)):
                    operations_containing.append(c)
            
            for c in operations_containing:
                c.initialise_operation()
                
            operations_with_ch_gives = []
            for c in operations_containing:
                gives = c.get_gives()
                for g in gives :
                    if(containg(g, ch)):
                        operations_with_ch_gives.append(c)

            new= ''
            for c in operations_with_ch_gives:
                string=''
                if c.get_full_string() != None :
                    string = c.get_full_string()
                else:
                    string = c.get_string()
                new += string+' + '
                self.operations.remove(c)            
            
            name= 'OPERATION_'+str(index)
            #print(name)
            index-=1
            operation= Operation(name, new)
            #print(new)
            origins_total, gives_total = [], []
            for c in operations_with_ch_gives:
                origins= c.get_origin()
                for o in origins:
                    origins_total.append(o)
                gives= c.get_gives()
                for g in gives:
                    gives_total.append(g)

            
                
            origins_total = remove_duplicates(origins_total)
            gives_total = remove_duplicates(gives_total)
            try:
                origins_total.remove([ch, 'P'])
            except:
                None
            #print(origins_total, gives_total)

            operation.set_total_gives(gives_total)
            operation.set_total_origin(origins_total)
            operation.set_initia()

            self.operations.append(operation)


        


    def initialise_operations(self):
        for c in self.operations:
            c.initialise_operation()
    
    def get_number_operations(self):
        return len(self.operations)
            

    def get_all_defined_channels(self):
        tab=[]
        for c in self.operations:
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

    def extract_analyse_operations(self):
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
                end= self.get_end_operation(start)
                code= self.string[start:end]
                #print(code)
                #print(code)
                name= 'OPERATION_'+str(index)
                self.operations.append(Operation(name, code))
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
                        end= self.get_end_operation(match.span(0)[1], 0, 1)
                    elif(self.string[match.span(0)[1]-1]=='{'):
                        end= self.get_end_operation(match.span(0)[1], 1, 0)
                    else: 
                        raise Exception("Don't know what i'm looking at..")
                    name= 'OPERATION_'+str(index)
                    code= self.string[start:end]
                    self.operations.append(Operation(name, code))
                    index+=1

                    changed=True
                    self.string= self.string.replace(code, name, 1)
                    break

        #=================================================================
        #THIRD PART: LINK THE TYPES CHANNEL THAT ARE DEFINED AS ... = OPERATION_ID
        #=================================================================
        self.link_operations_set()
        self.find_problematic_operations()
        self.initialise_operations()


        #=================================================================
        #FOURTH PART: LINK THE TYPES CHANNEL THAT ARE DEFINED AS ... = ...
        #=================================================================
        #Get all the occurence of word = word
        pattern= r'\w+ *= *\w+\s'
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
            if(right != left):
                if (is_in(tab_all_definied_channels, right) or is_in(tab_all_definied_inputs_outputs, right)):
                    #print('her')
                    name= 'OPERATION_'+str(index)
                    code= c
                    temp_operation= Operation(name, code)
                    temp_operation.not_normal()
                    self.operations.append(temp_operation)
                    index+=1
                    tab_all_definied_channels.append(left)
        for c in self.operations:
            self.string= self.string.replace(c.get_string(), c.get_id(), 1)
        self.initialise_operations()


    def print_operations(self):
        for c in self.operations:
            print(c.get_id(), 'string :', c.get_full_string())
            print(c.get_id(), 'origin :',  c.get_origin())
            print(c.get_id(), 'gives  :',  c.get_gives())

    def save_operations(self, name='operations_extracted'):
        myText = open(name+'.nf','w')
        for c in self.operations:
            #myText.write(str(c.get_gives())+' <- '+c.get_string()+'\n\n')
            myText.write(c.get_id()+ ' string : '+c.get_full_string()+'\n')
            myText.write(c.get_id()+' origin : '+  str(c.get_origin())+'\n')
            myText.write(c.get_id() +' gives  : '+  str(c.get_gives())+'\n\n\n')
        myText.close()

    def get_operations_formated(self):
        temp=""
        for c in self.operations:
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

    #Removes the functions from the workflow string
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

    #Finds/ Analyzes and formats the functions
    def clean_function(self):
        self.find_functions()
        self.format_functions()
    





    #===========================================
    #METHODS to manipulate ifs
    #===========================================
    
    #Method that replaces the condition ‘a = c1 ? val1 : val2’ by ‘if(c1){ a=val1 } else{ a=val2 }’
    def clean_up_if_double_dots_question_2(self):
        pattern= r'([^\=\n]+)\s*=\s*([^\?\n]+)\s*\?([^\n]+)'
        to_be_added=[]
        for match in re.finditer(pattern, self.string):
            variable = match.group(1)
            condition = match.group(2)
            #We have to identify the 2 different cases (values) by 'hand' because there can be a ':' in a paranthesis for example
            #We can't use a regex pattern
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
                    condition_true= s[start:i].strip()
                    condition_false= s[i+1:end].strip()
                    break
                i+=1
            #Replace the old string by the new one
            new_string="if ("+condition+") { \n"+variable+" = "+condition_true+"\n } else { \n"+variable+" = "+condition_false+"\n } "
            to_be_added.append([match.group(0), new_string])
        for a in to_be_added:
            self.string= self.string.replace(a[0], a[1])






    #===========================================
    #METHODS STRUCTURE
    #===========================================
    
    #Method that add an edge to the graph given 
    def create_edge(self, dot, l1, l2, la):
        dot.edge(l1, l2, constraint='true', label='')

    #Method that adds nodes to the graph with the corresponding type
    def create_node_type(self, dot, id, name, type):
        # P for Pointer -> like the name of the variable -> Red
        # V for Value -> like 1, 2, 'a', [4, 5, 6] -> Green
        # A for Adress -> like /data/some/bigfile.txt -> Purple
        # S for queries the NCBI SRA -> Orange
        name=id[len('OPERATION_'):]
        self.nb_nodes_operation+=1
        if(type=='A'):
            dot.node(id, name, color= '4', shape='doublecircle')#Purple
        elif(type=='V'):
            dot.node(id, name, color= '3', shape='doublecircle')#Green 
        elif(type=='S'):
            dot.node(id, name, color= '5', shape='doublecircle')#Orange
        elif(type=='P'):
            dot.node(id, name, color= '1', shape='doublecircle')#Red
        elif(type=='F'):
            dot.node(id, name, color= '6', shape='doublecircle')#Yellow

    #Method that reconstructs the structure of a workflow from the information extracted
    def get_structure(self,name='structure_worklow'):
        if(self.can_analyse):
            #Start by defining the graphviz diagram
            dot = graphviz.Digraph(filename=name, format='png', comment='structure', node_attr={'colorscheme': 'pastel19', 'style': 'filled'})
            
            #We start by creating 2 lists : tab_origin and tab_gives, 
            #every time that a node (either a process or an operation) 
            #is added to the graph the inputs of the node need to be added 
            #to tab_origin, and the outputs in tab_gives, the name of the 
            #node (either process or operation) also needs to be added to the 
            #list (more explicitly [‘key’, ‘name_node’] is added), these lists 
            #are to be used later on
            tab_origin, tab_gives= [], []

            #Start by adding all the inputs and outputs of the processes to the different lists
            for p in self.processes:
                input, output, _ = p.extractAll()
                for i in input:
                    _, name= i[0], i[1]
                    tab_origin.append([name, p.getName()])
                for o in output:
                    _, name= o[0], o[1]
                    tab_gives.append([name, p.getName()])
                #Adding the processes to the graph
                dot.node(p.getName(), p.getName(), color= '2', shape='box')#Blue
                self.nb_nodes_process +=1

            #Defining the list links_added which allows us to check if we have already added 
            #a link to the graph => it is just to avoid redundancies 
            links_added=[]
            
            #===============================================================
            #Case p.output -> p.input
            #===============================================================
            #For earch process
            for p1 in self.processes:
                #Get the outputs
                _, outputs_p1, _= p1.extractAll()
                #For the other processes
                for p2 in self.processes:
                    #Check it's not the same process
                    if(p1!=p2):
                        #Get the inputs 
                        inputs_p2, _, _= p2.extractAll()
                        #For each inputs and outputs for both processes
                        for output_p1_for in outputs_p1:
                            _, output_p1= output_p1_for[0], output_p1_for[1]
                            for input_p2_for in inputs_p2:
                                _, input_p2= input_p2_for[0], input_p2_for[1]
                                #check if the link matches
                                if(output_p1== input_p2):
                                    reference='{}:{} -> {}:{}'.format(p1.getName(),output_p1 , p2.getName(), input_p2)
                                    #Check that we've not already added it to the graph
                                    if(not check_containing(reference, links_added)):
                                        #Adding it to the graph and to the list
                                        links_added.append(reference)
                                        self.create_edge(dot, p1.getName(), p2.getName(), output_p1)
                                        self.nb_edges+=1
            
            #The next step is starting from the inputs and outputs from the different processes and linking the rest of the structure from that
            added_link= True
            operations_added=[]
            while(added_link):
                added_link = False

                #===========================================
                #From the origin tab :
                #===========================================
                #For every element o in origin_tab, 
                #we are searching for an element e which can link with o, 
                #such as e gives o (e -> o)
                new_operations_added=[]
                for origin in tab_origin:
                    origin_name, node_name= origin[0], origin[1]

                    #We start by searching if a channel given by an operation can link with the origin
                    #For every operation
                    for c in self.operations:
                        #Retrieve the channel that it gives (output)
                        c_gives= c.get_gives()
                        #For every one of its gives
                        for c_gives_for in c_gives:
                            #Get it's type + ID/Name
                            c_name, type_c=  c_gives_for[0], c_gives_for[1]
                            #If it's a pointer type (it should always be a pointer for gives)
                            #But there is no harm in checking
                            if(type_c=='P'):
                                #If the link can be made 
                                if(c_name== origin_name):
                                    #We check that it hasn't already been added
                                    reference='{}:{} -> {}:{}'.format(c.get_id(), c_name , node_name, origin_name)
                                    if(not check_containing(reference, links_added)):
                                        links_added.append(reference)
                                        #If the operation hasn't been added to the graph
                                        #It is added with its corresponding type
                                        if(not check_containing(c.get_id(), operations_added)):
                                            types=[]
                                            i=0
                                            for c_origin in c.get_origin():
                                                _, type_c_origin= c_origin[0], c_origin[1]
                                                types.append(type_c_origin)
                                            if(len(list(set(types)))!=1):
                                                if(is_in(types, 'P') or list(set(types))== []):
                                                    t='P'
                                                else: 
                                                    if(is_in(types, 'V')):
                                                        t='V'
                                                    else :
                                                        t=types[0]
                                            else:
                                                t= list(set(types))[0]
                                            self.create_node_type(dot, c.get_id(), c.get_string(), t)
                                            operations_added.append(c.get_id())
                                            new_operations_added.append(c)
                                        #The edge is added
                                        self.create_edge(dot, c.get_id(), node_name, c_name)
                                        self.nb_edges+=1
                                        added_link= True

                    #Searching if an output of a process can link with the origin
                    for p in self.processes:
                        if(p.getName()!=node_name):
                            #Get the inputs and outputs
                            _, outputs_p, _ = p.extractAll()
                            for output_p_full in outputs_p:
                                _, output_p= output_p_full[0], output_p_full[1]
                                #If the link can ve made
                                if(output_p== origin_name):
                                    reference='{}:{} -> {}:{}'.format(p.getName(), output_p, node_name, origin_name)
                                    #Check that we've not already added it to the graph
                                    if(not check_containing(reference, links_added)):
                                        #Adding it to the graph
                                        links_added.append(reference)
                                        self.create_edge(dot, p.getName(), node_name, output_p)
                                        self.nb_edges+=1
                                        added_link= True
                    
                #Can the newly added operation to tab_origin and tab_gives  
                for c in new_operations_added:
                    c_origin, c_gives= c.get_origin(), c.get_gives()
                    for o in c_origin:
                        if(o[1]=='P'):
                            tab_origin.append([o[0], c.get_id()])
                    for g in c_gives:
                        if(g[1]=='P'):
                            tab_gives.append([g[0], c.get_id()])    

                #===========================================
                #From the gives tab
                #===========================================
                #For every element g in gives_tab, 
                #we are searching for an element e which can link with g, 
                #such as g gives e (g -> e)
                new_operations_added=[]
                for gives in tab_gives:
                    gives_name, node_name= gives[0], gives[1]

                    #We start by searching if a channel origin by an operation can link with the gives
                    #For every operation
                    for c in self.operations:
                        #Retrieve the channel that it takes (origin/ input)
                        c_origin= c.get_origin()
                        #For every one of its origins
                        for c_origin_for in c_origin:
                            #Get it's type + ID/Name
                            c_name, type_c=  c_origin_for[0], c_origin_for[1]
                            #If it's a pointer type
                            if(type_c=='P'):
                                #If the link can be made
                                if(c_name== gives_name):
                                    #We check that it hasn't already been added
                                    reference='{}:{} -> {}:{}'.format(node_name, gives_name, c.get_id(), c_name)
                                    if(not check_containing(reference, links_added)):
                                        links_added.append(reference)
                                        #If the operation hasn't been added to the graph
                                        #It is added with its corresponding type (it is a pointer type : we have already checked)
                                        if(not check_containing(c.get_id(), operations_added)):
                                            self.create_node_type(dot, c.get_id(), c.get_string(), 'P')
                                            operations_added.append(c.get_id())
                                            new_operations_added.append(c)
                                        #The edge is added
                                        self.create_edge(dot,node_name, c.get_id(),c_name)
                                        self.nb_edges+=1
                                        added_link= True

                    #Searching if an input of a process can link with the gives
                    for p in self.processes:
                        if(p.getName()!=node_name):
                            #Get the inputs and outputs
                            inputs_p, _, _ = p.extractAll()
                            for input_p_full in inputs_p:
                                input_p_id, input_p_name= input_p_full[0], input_p_full[1]
                                if(input_p_name== gives_name):
                                    reference='{}:{} -> {}:{}'.format(node_name, gives_name, p.getName(),input_p_name )
                                    #Check that we've not already added it to the graph
                                    if(not check_containing(reference, links_added)):
                                        #Adding it to the graph
                                        links_added.append(reference)
                                        self.create_edge(dot, node_name, p.getName(),input_p_name)
                                        self.nb_edges+=1
                                        added_link= True
                
                #Can the newly added operation to tab_origin and tab_gives 
                for c in new_operations_added:
                    c_origin, c_gives= c.get_origin(), c.get_gives()
                    for o in c_origin:
                        if(o[1]=='P'):
                            tab_origin.append([o[0], c.get_id()])
                    for g in c_gives:
                        if(g[1]=='P'):
                            tab_gives.append([g[0], c.get_id()]) 
            #Save the graph                  
            dot.render()
            dot.save()
        else:
            self.nb_edges = -1
            self.nb_nodes_process= -1
            self.nb_nodes_operation = -1


    #===========================================
    #GENERAL METHODS : TO SAVE
    #===========================================

    #Saves the number of nodes (the different types) and edges into a file
    def save_nb_nodes_edges(self):
        myText = open('nb_nodes_edges'+'.txt','w')
        myText.write(f'{self.nb_nodes_process} node_processes\n')
        myText.write(f'{self.nb_nodes_operation} node_operations\n')
        myText.write(f'{self.nb_edges} edges\n')
        myText.close()

    #Saves the the worklfow string (formated version) as a nextflow file
    def save_file(self, name='formated_workflow'):
        myText = open(name+'.nf','w')
        myText.write(self.string)
        myText.close()


    #===========================================
    #INITIALIZATION AND RUN
    #===========================================

    #Initialise the basic stuff for a mainDSL1 type
    def initialise(self):
        #STEP1
        self.initialise_basic_main()
        #Check that there is the same number of open curlies than closing curlies
        if(self.right_nb_curly()):
            #STEP2
            #Finds and adds the proccesses to the list of processes + analyses them
            self.find_processes()
            print(f'Extracted {self.get_nb_processes()} processes')
            self.format_processes()

            #STEP3
            #Finds and formats the function -> In DSL1 functions are not important to the structure to we 'remove' (format) them to simply the analysis
            self.clean_function()

            #STEP4
            #We have to do this to update the channels which are in the double dots -> otherwise the analyseur won't recongise them later on 
            self.clean_up_if_double_dots_question_2()

            #STEP5 
            #Finds and analyzes every operation and adds the channels to the list of channels
            self.extract_analyse_operations()
            print(f'Extracted {self.get_number_operations()} channels')
            
            #STEP6
            #Reconstructs the structure of the workflow from the information that has been extracted
            self.get_structure()
            print(f'Structure reconstructed')
            print(f'With {self.nb_nodes_process} processes, {self.nb_nodes_operation} operations and {self.nb_edges} edges')
            
            #STEP7
            #Save the information that has been extracted
            self.save_operations()
            self.save_processes()
            self.get_info_processes()
            self.save_nb_nodes_edges()

        else:
            raise Exception("WHEN A CURLY OPENS IT NEEDS TO BE CLOSED! : Didn't find the same number of open curlies then closing curlies")
        


