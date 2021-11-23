import re

# P for Pointer -> like the name of the variable
# V for Value -> like 1, 2, 'a', [4, 5, 6]

class Channel:
    def __init__(self, id, string):
        self.id = id
        self.string = string
        self.value = None 
        self.condition = None
        #Probably have to ignore empty()
        self.origin = [] #Nothing, other channel, path
        #The channel 
        self.gives= []

    
    def get_string(self):
        return self.string

    def get_id(self):
        return self.id

    def set_gives(self, name):
        self.gives.append(name)

    def get_gives(self):
        return self.gives

    def get_origin(self):
        return self.origin


    def get_first_word(self):
        for i in range(len(self.string)):
            if(self.string[i]=='.'):
                return self.string[:i].strip()

    def check_first_word(self):
        #IF the first word is not a channel
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
            self.origin.append([match.group(1), 'V'])
        
        #print(self.origin)
    
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
        pattern= r'\.\s*(into)\s*\{(\s*\w+\s*\;\s*(\w+\s*\;\s*)*\w+\s*|\s*(\w+)\s*)\}'
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
  
            

            

    #Maybe change the name to have the other cases
    def check_set(self):
        pattern= r'\.\s*set\s*{\s*(\w+)\s*}'
        for match in re.finditer(pattern, self.string):
            self.gives.append([match.group(1), 'P'])





    #FORK


    

    def initialise_channel(self):
        self.string= self.string.strip()
        self.check_first_word()
        self.check_set()
        #print(self.get_first_word())
        self.check_join()
        self.check_fork()
        None
        #DO_STUFF

def tests():
    #Channel.join(..) or others shoudn't work but we've added it anyway
    #It doesn't matter since we suppose that the workflow is written correctly
    #===================================================
    #join
    #===================================================
    test="left.join(right).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['left', 'P'], ['right', 'P']])

    test="Channel.join(right).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #merge
    #===================================================
    test="odds.merge( evens ).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P']])

    test="odds.merge( evens, george, and,the , penguin ).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P'], ['george', 'P'], ['and', 'P'], ['the', 'P'], ['penguin', 'P']])

    test="Channel.merge(right).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #mix
    #===================================================
    test="odds.mix( evens ).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P']])

    test="odds.mix ( evens, george, and,the , penguin ).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P'], ['george', 'P'], ['and', 'P'], ['the', 'P'], ['penguin', 'P']])

    test="Channel.mix(right).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #phase
    #===================================================
    test="left.phase (right).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['left', 'P'], ['right', 'P']])

    test="Channel.phase(right).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #cross
    #===================================================
    test="left.cross (right).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['left', 'P'], ['right', 'P']])

    test="Channel.cross(right).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #cross
    #===================================================
    test="left.combine (right).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['left', 'P'], ['right', 'P']])

    test="Channel.combine(right).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #mix
    #===================================================
    test="odds.concat( evens ).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P']])

    test="odds.concat ( evens, george, and,the , penguin ).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['odds', 'P'], ['evens', 'P'], ['george', 'P'], ['and', 'P'], ['the', 'P'], ['penguin', 'P']])

    test="Channel.concat(right).view()"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['right', 'P']])
    #===================================================
    #spread
    #===================================================
    test="Channel.from(1,2,3).spread(['a','b'])"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[["['a','b']", 'V']])
    #===================================================
    #choice
    #===================================================
    test="source.choice( queue1, queue2 ) { a -> a =~ /^Hello.*/ ? 0 : 1 }"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['source', 'P']])
    assert(c.get_gives()==[['queue1', 'P'], ['queue2', 'P']])

    test="Channel.choice( queue1, queue2 ) { a -> a =~ /^Hello.*/ ? 0 : 1 }"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[])
    assert(c.get_gives()==[['queue1', 'P'], ['queue2', 'P']])

    test="source.choice( queue1, queue2 , queue3) { a -> a =~ /^Hello.*/ ? 0 : 1 }"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['source', 'P']])
    assert(c.get_gives()==[['queue1', 'P'], ['queue2', 'P'], ['queue3', 'P']])
    #===================================================
    #into
    #===================================================
    test="Channel.from( 'a', 'b', 'c' ).into{ foo; bar }"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_gives()==[['foo', 'P'], ['bar', 'P']])

    test="(foo, bar) = Channel.from( 'a','b','c').into(2)"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_gives()==[])
    #===================================================
    #seperate
    #===================================================
    test="Channel.from ( 2,4,8 ).separate( queue1, queue2 ) { a -> [a+1, a*a] }"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_gives()==[['queue1', 'P'], ['queue2', 'P']])

    test="source.separate(3) { a -> [a, a+1, a*a] }"
    c= Channel('penguin', test)
    c.initialise_channel()
    assert(c.get_origin()==[['source', 'P']])
    assert(c.get_gives()==[])
    #===================================================
    #tap
    #===================================================
    test="Channel.of ( 'a', 'b', 'c' ).tap ( log1 ).map { it * 2 }.tap ( log2 ).map { it.toUpperCase() }.view { 'Result: $it' }"
    c= Channel('penguin', test)
    c.initialise_channel()
    #print(c.get_gives())
    assert(c.get_gives()==[['log1', 'P'], ['log2', 'P']])

    test="Channel.of ( 'a', 'b', 'c' ).tap { log1 }.map { it * 2 }.tap { log2 }.map { it.toUpperCase() }.view { 'Result: $it' }"
    c= Channel('penguin', test)
    c.initialise_channel()
    #print(c.get_gives())
    assert(c.get_gives()==[['log1', 'P'], ['log2', 'P']])
 

if __name__ == "__main__":
    test="""
        Channel
            .fromFilePairs( input, size: 1 )
            .filter { it =~/.*.bam/ }
            .map { row -> [ row[0], [ row[1][0] ] ] }
            .ifEmpty { exit 1, "[nf-core/eager] error: Cannot find any bam file matching: ${input}" }
            .set { ch_reads_for_faketsv }
        """
    c= Channel('channel_1', test)
    #c.initialise_channel()

    tests()

        