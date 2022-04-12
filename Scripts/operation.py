# Nextflow Analyzer
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022

import re

# P for Pointer -> like the name of the variable
# V for Value -> like 1, 2, 'a', [4, 5, 6]
# A for Adress -> like /data/some/bigfile.txt
# S for queries the NCBI SRA 

class Operation:
    def __init__(self, id, string):
        self.id = id
        self.string = string
        self.full_string = None
        self.value = None 
        self.condition = None
        #We use this attribute to ddistingue 2 cases the normal case and the last case OPERATION_x = OPERATION_y
        self.normal = True
        #Probably have to ignore empty()
        self.origin = [] #Nothing, other channel, path
        #The channel 
        self.gives = []
        self.intia = False

    def not_normal(self):
        self.normal = False

    def get_string(self):
        return self.string

    def set_full_string(self, string):
        self.full_string= string
    
    def get_full_string(self):
        return self.full_string

    def get_id(self):
        return self.id

    def set_gives(self, name):
        self.gives.append(name)

    def get_gives(self):
        return self.gives

    def get_origin(self):
        return self.origin

    def set_total_gives(self, li):
        self.gives= li
    
    def set_total_origin(self, li):
        self.origin= li

    def set_initia(self):
        self.intia = True
        self.full_string= self.string



    def get_first_word(self):
        for i in range(len(self.string)):
            if(self.string[i]=='.' or self.string[i]==' '):
                return self.string[:i].strip()

    def check_first_word(self):
        #IF the first word is not a channel
        #if(self.string[:7]!='Channel' and self.string[:7]!='channel'):
        if(self.get_first_word()!='Channel' and self.get_first_word()!='channel'):
            self.origin.append([self.get_first_word(), 'P']) 

    #For every case i have checked by compilying the nextflow code for each operator
    #join in the name of the method doesn't reference the join operator but the action of 'joining' channels together
    def check_join(self):
        #================================
        #join/ phase/ cross/ combine
        #================================
        pattern= r'\.\s*(join|phase|cross|combine)\s*\(\s*(\w+)\s*\)'
        for match in re.finditer(pattern, self.string):
            self.origin.append([match.group(2), 'P'])
        #================================
        #merge/ mix/ concat
        #================================
        pattern= r'\.\s*(merge|mix|concat)\s*\((\s*\w+\s*\,\s*(\w+\s*\,\s*)*\w+\s*|\s*(\w+)\s*)\)'
        for match in re.finditer(pattern, self.string):
            temp=match.group(2)
            temp= temp.split(',')
            for t in temp:
                t= t.strip()
                self.origin.append([t, 'P'])
        #================================
        #spread
        #================================
        pattern= r'\.\s*spread\s*\(([\s\w\.(),\"\'\{\}\[\]+-]+)\)'
        for match in re.finditer(pattern, self.string):
            self.origin.append([match.group(1).strip(), 'V'])
        #print(self.origin)
    
    #From the website: "Channels may be created implicitly by the process output(s) declaration or explicitly using the following channel factory methods."
    #Bug Possible here: if there is () in value => il ne le reconnetra pas
    #Another bug if there is () a fromPath or \n
    def check_factory(self):
        #================================
        #of/ from/ value/ fromList
        #================================
        pattern= r'\.\s*(of|from|value|fromList)\s*\(([\s\w\.,;\"\'\{\}\[\]+-]*)\)'
        for match in re.finditer(pattern, self.string):
            #print('test',match.group(1))
            self.origin.append([match.group(2).strip(), 'V'])
        #================================
        #fromPath/ fromFilePairs
        #================================
        pattern= r'.\s*(fromPath|fromFilePairs|watchPath)\s*\(([^\)\n]*)\)'
        for match in re.finditer(pattern, self.string):
            #print('test',match.group(1))
            self.origin.append([match.group(2).strip(), 'A'])
        #================================
        #fromSRA
        #================================
        pattern= r'.\s*fromSRA\s*\(([^\)\n]*)\)'
        for match in re.finditer(pattern, self.string):
            #print('test',match.group(1))
            self.origin.append([match.group(1).strip(), 'S'])
        #================================
        #Bind VERSION1 myChannel.bind( 'Hello world' )
        #================================
        pattern= r'.\s*bind\s*\(([^\)\n]*)\)'
        for match in re.finditer(pattern, self.string):
            #print('test',match.group(2))
            self.origin.append([match.group(1).strip(), 'V'])
        #================================
        #Bind VERSION2 myChannel << 'Hello world'
        #================================    
        pattern= r'(<<)\s*([^\n]*)'
        #We do this in cas a '<<' is in a mapor another operator
        for match in re.finditer(pattern, self.string):
            i= match.span(1)[0]
            curly, para=0, 0
            while(i<len(self.string)):
                if(self.string[i]=='{' or self.string[i]=='}'):
                    curly+=1
                elif(self.string[i]=='(' or self.string[i]==')'):
                    para+=1
                i+=1
            if(curly%2==0 and para%2==0):
                #print('test',match.group(1))
                self.origin.append([match.group(2).strip(), 'V'])

            
    
    def check_fork(self):
        #================================
        #choice
        #================================
        pattern= r'\.\s*(choice)\s*\((\s*\w+\s*\,\s*(\w+\s*\,\s*)*\w+\s*|\s*(\w+)\s*)\)'
        for match in re.finditer(pattern, self.string):
            temp=match.group(2)
            temp= temp.split(',')
            for t in temp:
                t= t.strip()
                self.gives.append([t, 'P'])
        #================================
        #into VERSION 1
        #================================
        pattern= r'\.\s*(into)\s*\{(\s*\w+\s*\;\s*(\w+\s*\;\s*)*\w*\s*|\s*(\w+)\s*)\}'
        for match in re.finditer(pattern, self.string):
            temp=match.group(2)
            temp= temp.split(';')
            for t in temp:
                t= t.strip()
                self.gives.append([t, 'P'])
        #================================
        #into VERSION 2
        #================================
        #For the case (foo, bar) = Channel.from( 'a','b','c').into(2)
        #We don't have to worry about the (foo, bar) because that is already delt with in the extract_channels method 
        pattern= r'\.\s*(into)\s*\(\s*(\d+)\s*\)'
        for match in re.finditer(pattern, self.string):
            nb= int(match.group(2))
        #================================
        #seperate 
        #================================
        pattern= r'\.\s*(separate)\s*\((\s*\w+\s*\,\s*(\w+\s*\,\s*)*\w+\s*|\s*(\w+)\s*)\)'
        for match in re.finditer(pattern, self.string):
            #For the case (queue1, queue2, queue3) = source.separate(3) { a -> [a, a+1, a*a] }
            #We don't have to worry about the (queue1, queue2, queue3) because that is already delt with in the extract_channels method 
            try:
                nb= int(match.group(2))
                #print(nb)
            except:
                temp=match.group(2)
                temp= temp.split(',')
                for t in temp:
                    t= t.strip()
                    self.gives.append([t, 'P'])
        #================================
        #tap VERSION1 ()
        #================================
        #pattern= r'\.\s*tap\s*\(\s*(\w+)\s*\)|\.\s*tap\s*\{\s*(\w+)\s*\}'
        pattern= r'\.\s*tap\s*\(\s*(\w+)\s*\)'
        for match in re.finditer(pattern, self.string):
            #print(match.group(1))
            self.gives.append([match.group(1), 'P'])
        #================================
        #tap VERSION2 {}
        #================================
        pattern= r'\.\s*tap\s*\{\s*(\w+)\s*\}'
        for match in re.finditer(pattern, self.string):
            #print(match.group(1))
            self.gives.append([match.group(1), 'P'])
          
    def check_set(self):
        pattern= r'\.\s*set\s*{\s*(\w+)\s*}'
        for match in re.finditer(pattern, self.string):
            self.gives.append([match.group(1), 'P'])

    def extract_affectation(self):
        pattern= r'(\w+) *= *(\w+)'
        for match in re.finditer(pattern, self.string):
            self.gives.append([match.group(1), 'P'])
            self.origin.append([match.group(2), 'P'])

    def check_same_value(self):
        tab_to_remove=[]
        for o in self.origin:
            for g in self.gives:
                if(o[0]==g[0]):
                    tab_to_remove.append(o)
        print(self.origin)
        for t in tab_to_remove:
            self.origin= self.origin.remove(t)
        print(self.origin)
    

    def initialise_operation(self):
        if(not self.intia):
            self.string= self.string.strip()
            if(self.full_string==None):
                self.set_full_string(self.string)
            if(self.normal):
                self.check_first_word()
                self.check_set()
                #print(self.get_first_word())
                self.check_join()
                self.check_fork()
                self.check_factory()
            else:
                self.extract_affectation()
            self.intia=True
        #self.check_same_value()

        #DO_STUFF

def tests():
    #Channel.join(..) or others shoudn't work but we've added it anyway
    #It doesn't matter since we suppose that the workflow is written correctly
    #===================================================
    #join
    #===================================================
    test="left.join(right).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['left', 'P'], ['right', 'P']])

    test="Channel.join(right).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #merge
    #===================================================
    test="odds.merge( evens ).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P']])

    test="odds.merge( evens, george, and,the , penguin ).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P'], ['george', 'P'], ['and', 'P'], ['the', 'P'], ['penguin', 'P']])

    test="Channel.merge(right).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #mix
    #===================================================
    test="odds.mix( evens ).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P']])

    test="odds.mix ( evens, george, and,the , penguin ).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P'], ['george', 'P'], ['and', 'P'], ['the', 'P'], ['penguin', 'P']])

    test="Channel.mix(right).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #phase
    #===================================================
    test="left.phase (right).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['left', 'P'], ['right', 'P']])

    test="Channel.phase(right).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #cross
    #===================================================
    test="left.cross (right).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['left', 'P'], ['right', 'P']])

    test="Channel.cross(right).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #cross
    #===================================================
    test="left.combine (right).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['left', 'P'], ['right', 'P']])

    test="Channel.combine(right).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #mix
    #===================================================
    test="odds.concat( evens ).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P']])

    test="odds.concat ( evens, george, and,the , penguin ).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P'], ['george', 'P'], ['and', 'P'], ['the', 'P'], ['penguin', 'P']])

    test="Channel.concat(right).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #spread
    #===================================================
    test="Channel.from(1,2,3).spread(['a','b'])"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["['a','b']", 'V'], ["1,2,3", 'V']])
    #===================================================
    #choice
    #===================================================
    test="source.choice( queue1, queue2 ) { a -> a =~ /^Hello.*/ ? 0 : 1 }"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['source', 'P']])
    assert(c.get_gives()==[['queue1', 'P'], ['queue2', 'P']])

    test="Channel.choice( queue1, queue2 ) { a -> a =~ /^Hello.*/ ? 0 : 1 }"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[])
    assert(c.get_gives()==[['queue1', 'P'], ['queue2', 'P']])

    test="source.choice( queue1, queue2 , queue3) { a -> a =~ /^Hello.*/ ? 0 : 1 }"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['source', 'P']])
    assert(c.get_gives()==[['queue1', 'P'], ['queue2', 'P'], ['queue3', 'P']])
    #===================================================
    #into
    #===================================================
    test="Channel.from( 'a', 'b', 'c' ).into{ foo; bar }"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_gives()==[['foo', 'P'], ['bar', 'P']])
    assert(c.get_origin()==[["'a', 'b', 'c'", 'V']])

    test="Channel.from( 'a','b','c').into(2)"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_gives()==[])
    assert(c.get_origin()==[["'a','b','c'", 'V']])
    #===================================================
    #seperate
    #===================================================
    test="Channel.from ( 2,4,8 ).separate( queue1, queue2 ) { a -> [a+1, a*a] }"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_gives()==[['queue1', 'P'], ['queue2', 'P']])
    assert(c.get_origin()==[["2,4,8", 'V']])

    test="source.separate(3) { a -> [a, a+1, a*a] }"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['source', 'P']])
    assert(c.get_gives()==[])
    #===================================================
    #tap
    #===================================================
    test="Channel.of ( 'a', 'b', 'c' ).tap ( log1 ).map { it * 2 }.tap ( log2 ).map { it.toUpperCase() }.view { 'Result: $it' }"
    c= Operation('penguin', test)
    c.initialise_operation()
    #print(c.get_gives())
    assert(c.get_gives()==[['log1', 'P'], ['log2', 'P']])

    test="Channel.of ( 'a', 'b', 'c' ).tap { log1 }.map { it * 2 }.tap { log2 }.map { it.toUpperCase() }.view { 'Result: $it' }"
    c= Operation('penguin', test)
    c.initialise_operation()
    #print(c.get_gives())
    assert(c.get_gives()==[['log1', 'P'], ['log2', 'P']])
    #===================================================
    #of
    #===================================================
    test="Channel.of(1, 4, 6, 7, 8)"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['1, 4, 6, 7, 8', 'V']])
    #===================================================
    #value
    #===================================================
    test="Channel.value()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['', 'V']])

    test="Channel.value( 'Hello there' )"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["'Hello there'", 'V']])

    test="Channel.value( [1,2,3,4,5] )"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[['[1,2,3,4,5]', 'V']])
    #===================================================
    #fromList
    #===================================================
    test="Channel.fromList( ['a', 'b', 'c', 'd'] ).view { 'value: $it' }"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["['a', 'b', 'c', 'd']", 'V']])
    #===================================================
    #fromPath
    #===================================================
    test="Channel.fromPath( '/data/some/bigfile.txt' )"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["'/data/some/bigfile.txt'", 'A']])

    test="Channel.fromPath( '/data/big/*.txt' )"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["'/data/big/*.txt'", 'A']])

    test="Channel.fromPath( 'data/file_{1,2}.fq' )"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["'data/file_{1,2}.fq'", 'A']])

    test="Channel.fromPath( ['/some/path/*.fq', '/other/path/*.fastq'] )"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["['/some/path/*.fq', '/other/path/*.fastq']", 'A']])
    #===================================================
    #fromFilePairs
    #===================================================
    test="Channel.fromFilePairs('/my/data/SRR*_{1,2}.fastq')"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["'/my/data/SRR*_{1,2}.fastq'", 'A']])

    test="Channel.fromFilePairs('/some/data/*', size: -1) { file -> file.extension }"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["'/some/data/*', size: -1", 'A']])
    #===================================================
    #fromSRA
    #===================================================
    test="Channel.fromSRA('SRP043510').view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["'SRP043510'", 'S']])

    test="Channel.fromSRA(ids).view()"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["ids", 'S']])
    #===================================================
    #watchPath
    #===================================================
    test="Channel.watchPath( '/path/*.fa' ).subscribe { println 'Fasta file: $it' }"
    c= Operation('penguin', test)
    c.initialise_operation()
    assert(c.get_origin()==[["'/path/*.fa'", 'A']])
    #===================================================
    #Bind
    #===================================================
    test="Channel.bind( 'Hello world' )"
    c= Operation('penguin', test)
    c.initialise_operation()
    #print(c.get_origin())
    assert(c.get_origin()==[["'Hello world'", 'V']])

    test="Channel << 'Hello world' "
    c= Operation('penguin', test)
    c.initialise_operation()
    #print(c.get_origin())
    assert(c.get_origin()==[["'Hello world'", 'V']])

    test="my_channel << 'Hello world' "
    c= Operation('penguin', test)
    c.initialise_operation()
    #print(c.get_origin())
    assert(c.get_origin()==[["my_channel", 'P'], ["'Hello world'", 'V']])
    

        
