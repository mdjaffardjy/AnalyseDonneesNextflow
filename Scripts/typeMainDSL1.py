# Nextflow Analyzer
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022

import re
import os
import graphviz
import json

from .typeMain import * 
from .process import *
from .function import *
from .channel import *
from .utility import *


class TypeMainDSL1(TypeMain):
    def __init__(self, address):
        super().__init__(address)
        self.processes=[]
        self.functions=[]
        self.channels=[]
        self.added_operators= []

        self.can_analyse=True
        self.analyze_processes = True
        self.name_workflow = ''
        
        self.nb_edges = 0
        self.nb_nodes_process = 0
        self.nb_nodes_operation = 0
        


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

    def get_name_workflow(self):
        t = os.getcwd()
        i=-1
        while(t[i] != '/'):
            i-=1
        self.name_workflow = t[(i+1):len(t)]
        return self.name_workflow




    #===========================================
    #METHODS FOR MANIPULATING PROCESSES
    #===========================================
    #Finds and adds the processes to the list of processes + analyses them
    def find_processes(self):
        pattern=  r'([^\w]?process\s+\w+\s*{)'
        for match in re.finditer(pattern, self.string):
            start= match.span()[0]
            end= self.extract_curly(match.span()[1])
            process= Process(self.string[start:end])
            process.extractProcess(analyse_tools=self.analyze_processes)
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

    #Removes the processes from the workflow string (this simplifies the analysis)
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
    
    def save_processes(self, name='processes_extracted'):
        myText = open(name+'.nf','w')
        for p in self.processes:
            #myText.write(str(c.get_gives())+' <- '+c.get_string()+'\n\n')
            myText.write('Name : '+p.getName()+'\n')
            input, output, emit= p.extractAll()
            myText.write('Inputs : '+  str(input)+'\n')
            myText.write('Outputs : '+  str(output)+'\n')
            myText.write('Emits : '+  str(emit)+'\n\n\n')
        myText.close()
    
    #Return the processes found
    def get_processes(self):
        return self.processes

    
    def get_info_processes(self, name='processes_info'):
        if(self.analyze_processes):
            dict={}
            #For each process we get it's corresponding data
            for p in self.processes:
                dict[p.getName()] = {}
                dict[p.getName()]['name_process']= p.getName()
                def get_number_lignes(string):
                    nb=0
                    for s in string:
                        if(s=='\n'):
                            nb+=1
                    return nb 
                dict[p.getName()]['string_process']= p.get_string()
                #We remove one since we do not want the definition ligne to count : not really really important
                dict[p.getName()]['nb_lignes_process']= get_number_lignes(p.get_string())-1
                dict[p.getName()]['string_script']= p.get_string_script()
                #In this case we leave the ligne corresponding to """ since they all have it => it doesn't matter
                dict[p.getName()]['nb_lignes_script']= get_number_lignes(p.get_string_script())
                dict[p.getName()]['language_script']= p.getScriptLanguage()
                dict[p.getName()]['tools']= p.getListTools()
                dict[p.getName()]['tools_url'] = p.getListToolsUrl()
                dict[p.getName()]['tools_dico'] = p.getListAnnotationsTools()
                inputs, outputs, emits=p.extractAll()
                def simplify(tab):
                    temp=[]
                    for t in tab:
                        temp.append(t[1])
                    return temp
                dict[p.getName()]['inputs']= simplify(inputs)
                dict[p.getName()]['nb_inputs']= len(inputs)
                dict[p.getName()]['outputs']= simplify(outputs)
                dict[p.getName()]['nb_outputs']= len(outputs)

                dict[p.getName()]['name_workflow']= self.get_name_workflow()
                
                
                dict[p.getName()]['directive']= p.getDirectiveList()
                dict[p.getName()]['when']= p.getWhen()
                dict[p.getName()]['stub']= p.getStub()
            with open(name+'.json', "w") as outfile:
                json.dump(dict, outfile, indent=4)
        

    
    


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
    
    def find_problematic_channels(self):
        index=-1
        problematic_channels = []
        pattern = r'(\w+) *= *(\w+)'
        for c in self.channels:
            if c.get_full_string() != None :
                for match in re.finditer(pattern, c.get_full_string()):
                    if(match.group(1) == match.group(2)):
                        problematic_channels.append(match.group(1))
        
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

        for ch in problematic_channels:
            channels_containing = []
            for c in self.channels:
                string=''
                if c.get_full_string() != None :
                    string = c.get_full_string()
                else:
                    string = c.get_string()
                if(is_in(string, ch)):
                    channels_containing.append(c)
            
            for c in channels_containing:
                c.initialise_channel()
                
            operations_with_ch_gives = []
            for c in channels_containing:
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
                self.channels.remove(c)            
            
            name= 'CHANNEL_'+str(index)
            #print(name)
            index-=1
            channel= Channel(name, new)
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

            channel.set_total_gives(gives_total)
            channel.set_total_origin(origins_total)
            channel.set_initia()

            self.channels.append(channel)

            #print(self.channels[-1].get_id())

        


    def initialise_channels(self):
        for c in self.channels:
            c.initialise_channel()
    
    def get_number_channels(self):
        return len(self.channels)
            

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
        self.find_problematic_channels()
        self.initialise_channels()


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

    def save_channels(self, name='channels_extracted'):
        myText = open(name+'.nf','w')
        dico = {}
        for c in self.channels:
            #myText.write(str(c.get_gives())+' <- '+c.get_string()+'\n\n')
            myText.write(c.get_id()+ ' string : '+c.get_full_string()+'\n')
            myText.write(c.get_id()+' origin : '+  str(c.get_origin())+'\n')
            myText.write(c.get_id() +' gives  : '+  str(c.get_gives())+'\n\n\n')

            dico[c.get_id()] = {}
            dico[c.get_id()]['string'] = c.get_full_string()
            dico[c.get_id()]['origin'] = c.get_origin()
            dico[c.get_id()]['gives'] = c.get_gives()

        myText.close()

        with open(name+'.json', "w") as outfile:
                json.dump(dico, outfile, indent=4)


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
                    condition_true= s[start:i].strip()
                    condition_false= s[i+1:end].strip()
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
        self.nb_nodes_operation+=1
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

    def get_structure_4(self,name='structure_worklow_4'):
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
                                                    if(is_in(types, 'V')):
                                                        t='V'
                                                    else :
                                                        t=types[0]
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
            dot.render()
            dot.save()
            self.nb_edges = nb_links
            self.nb_nodes_process= nb_process
        else:
            self.nb_edges = -1
            self.nb_nodes_process= -1
            self.nb_nodes_operation = -1













    #===========================================
    #GENERAL METHODS
    #===========================================
    def save_nb_nodes_edges(self):
        myText = open('nb_nodes_edges'+'.txt','w')
        myText.write(f'{self.nb_nodes_process} node_processes\n')
        myText.write(f'{self.nb_nodes_operation} node_operations\n')
        myText.write(f'{self.nb_edges} edges\n')
        myText.close()

    #Saves the the worklfow string in a given address as a nextflow file
    def save_file(self, name='formated_workflow'):
        myText = open(name+'.nf','w')
        myText.write(self.string)
        myText.close()



    #Initialise the basic stuff for a mainDSL1 type
    def initialise(self):
        #STEP1
        self.initialise_basic_main()
        #Check that there is the same number of open curlies than closing curlies
        if(self.right_nb_curly()):
            #STEP2
            #Finds and adds the proccesses to the list of processes + analyses them
            self.find_processes()
            #print(f'Extracted {self.get_nb_processes()} processes')
            self.format_processes()

            #STEP3
            #Finds and formats the function -> In DSL1 functions are not important to the structure to we 'remove' (format) them to simply the analysis
            self.clean_function()

            #STEP4
            #We have to do this to update the channels which are in the double dots -> otherwise the analyseur won't recongise them later on 
            self.clean_up_if_double_dots_question_2()


            #STEP5 
            #Find and analyse every channel and add them to the list of channels
            self.extract_analyse_channels()
            #print(f'Extracted {self.get_number_channels()} channels')
            
            self.get_structure_4()
            #print(f'Structure reconstructed')
            #print(f'With {self.nb_nodes_process} processes, {self.nb_nodes_operation} operations and {self.nb_edges} edges')
            
            self.save_channels()
            self.save_processes()
            self.get_info_processes()
            self.save_nb_nodes_edges()


        else:
            raise Exception("WHEN A CURLY OPENS IT NEEDS TO BE CLOSED! : Didn't find the same number of open curlies then closing curlies")
        


