
from logging import error
from typeMain import * 
import re
import graphviz
import random


class TypeMainDSL2(TypeMain):
    def __init__(self, address, root):
        super().__init__(address, root)
        self.processes=[]
        self.functions=[]
        self.channels=[]
        self.subworkflows=[]
        self.dot= None
    

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
    #METHODS FOR MANIPULATING THE GRAPH
    #===========================================
    def add_link(self, l1, l2, la=''):
        self.dot.edge(l1, l2, constraint='true', label=la)


    def create_node_type(self, dot, id, name, type):
        name=id[8:]
        if(type=='A'):
            dot.node(id, name, color= '4', shape='doublecircle')
        elif(type=='V'):
            dot.node(id, name, color= '3', shape='doublecircle')
        elif(type=='S'):
            dot.node(id, name, color= '5', shape='doublecircle')
        elif(type=='P'):
            dot.node(id, name, color= '1', shape='doublecircle')
        #FUNCTION
        elif(type=='F'):
            dot.node(id, name, color= '6', shape='doublecircle')





    #===========================================
    #METHODS FOR MANIPULATING WORKFLOWS
    #===========================================
    def find_workflows(self):
        pattern= r'workflow\s+(\w+)\s*{'
        i=0
        colors= ['brown', 'cornflowerblue', 'darkcyan', 'darkgreen', 'darkred', 'darkorange', 'darkmagenta', 'hotpink', 'green', 'powderblue', 'peru']
        random.shuffle(colors)
        for match in re.finditer(pattern, self.string):
            i+=1
            #print(self.string[match.span()[0]:match.span()[1]])
            print('name:', match.group(1))
            start= match.span()[0]
            end= self.extract_curly(match.span()[1])
            #print(self.string[start:end])
            with self.dot.subgraph(name='cluster_'+match.group(1)) as c:
                c.attr(label=match.group(1), color=colors[i%len(colors)])
                #TODO => analyse the inside of the workflow
                c.edges([('a'+str(i)+'_1', 'a'+str(i+1)+'_2')])
    


    """
    IMPORTANT: I think that i don't actually have to analysz take and emit since we supposing that the code is written correctly
    """
    #Takes are obligatory channels
    def get_takes_workflow(self, workflow):
        pattern_take, start_take, end_take= r'take *:', 0, 0
        pattern_main, start_main, end_main= r'main *:', 0, 0
        pattern_emit, start_emit, end_emit= r'emit *:', 0, 0

        for match in re.finditer(pattern_take, workflow):
            start_take, end_take= match.span()[0], match.span()[1]
        for match in re.finditer(pattern_main, workflow):
            start_main, end_main= match.span()[0], match.span()[1]
        for match in re.finditer(pattern_emit, workflow):
            start_emit, end_emit= match.span()[0], match.span()[1]

        def extract_take(start, end):
            tab_take = workflow[start:end].split('\n')
            tab_take = [t.strip() for t in tab_take]
            tab_take = [t for t in tab_take if t != '']
            return tab_take

        #Case there is no take
        if(start_take==0 and end_take==0):
            return []
        #Case there is a main
        elif(start_main !=0 and end_main !=0):
            return extract_take(end_take, start_main)
        #Case there is an emit
        elif(start_emit !=0 and end_emit !=0):
            return extract_take(end_take, start_emit)
        #Case just take
        else:
            return extract_take(end_take, len(workflow)-1)
    
    def get_emits_workflow(self, workflow):
        pattern_emit, start_emit, end_emit= r'emit *:', 0, 0

        for match in re.finditer(pattern_emit, workflow):
            start_emit, end_emit= match.span()[0], match.span()[1]
        
        #Case there is no emit
        if(start_emit==0 and end_emit==0):
            return []
        else:
            tab_emit = workflow[end_emit:len(workflow)-1].split('\n')
            tab_emit = [t.strip() for t in tab_emit]
            tab_emit = [t for t in tab_emit if t != '']
            return tab_emit





    def find_main_workflow(self):
        pattern= r'workflow\s*{'
        i=0
        start, end=0, 0
        for match in re.finditer(pattern, self.string):
            i+=1
            start= match.span()[0]
            end= self.extract_curly(match.span()[1])
            print(self.string[start:end])
        if(i>1):
            raise Exception("Multiple 'main' workflows found")
        #TODO => analyse the workflow
        main_workflow= self.string[start:end]
        print('takes:', self.get_takes_workflow(main_workflow))
        for t in self.get_takes_workflow(main_workflow):
            self.add_link(t, 'main')
        self.dot.node('data', 'data', color= '1', shape='doublecircle')
        """
        pattern_take, start_take, end_take= r'take *:', 0, 0
        pattern_main, start_main, end_main= r'main *:', 0, 0
        pattern_emit, start_emit, end_emit= r'emit *:', 0, 0
        for match in re.finditer(pattern_take, workflow):
            start_take, end_take= match.span()[0], match.span()[1]
        for match in re.finditer(pattern_main, workflow):
            start_main, end_main= match.span()[0], match.span()[1]
        for match in re.finditer(pattern_emit, workflow):
            start_emit, end_emit= match.span()[0], match.span()[1]
        print(start_take, end_take)
        tab_take = workflow[end_take:start_main].split('\n')
        for t in range(len(tab_take)):
            tab_take[t] = tab_take[t].strip()
        tab_take= [t for t in tab_take if t != '']
        print(tab_take)
        print(start_main, end_main)
        print(start_emit, end_emit)
        """
        





    def get_imports(self):
        pattern_simple= r'include *{ *(\w+) *} *from *([^\n ]+)'
        pattern_as= r'include *{ *(\w+) +as +(\w+) *} *from *([^\n ]+)'
        for match in re.finditer(pattern_simple, self.string):
            print(f'Include {match.group(1)} From {match.group(2)}')
        print('\n')
        for match in re.finditer(pattern_as, self.string):
            print(f'Include {match.group(1)} As {match.group(2)}  From {match.group(3)}')
    
    def initialise(self):
        self.initialise_basic_main()
        self.dot = graphviz.Digraph(filename='structure_worklow_DSL2', format='png', comment='structure'\
                            , node_attr={'colorscheme': 'pastel19', 'style': 'filled'})
        self.get_imports()
        None
    
    def save_structure(self, address= "/home/george/Bureau/TER/"):
        self.dot.render(directory=address)
        self.dot.save(directory=address)


#=================
#IF USED AS A MAIN
#=================
if __name__ == "__main__":
    m= TypeMainDSL2("/home/george/Bureau/TER/test_dsl2.nf", "/home/george/Bureau/TER/")
    m.initialise()
    m.find_main_workflow()
    m.find_workflows()

    m.save_structure()
    
    #print("I shoudn't be executed as a main")
