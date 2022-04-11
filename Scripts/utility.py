import re

def is_in(tab, ele):
    for e in tab:
        if (e==ele):
            return True
    return False


#For all functions use test_utilities.py to see examples of how they work 

def print_in_red(text):
    print('\x1b[0;37;41m' + text + '\x1b[0m')

#Function that checks if element is in list
def check_containing(ele, tab):
    index   = tab.count(ele)
    if(index==0):
        return False
    return True

#Function that returns an empty string of the same forme as the string[start:end]
def create_empty(string, start, end):
    empty=''
    for i in range(start, end):
        if(string[i]=='\n'):
            empty+='\n'
        else:
            empty+=' '
    return empty

#Function that returns the next character (+ it's index)
def get_next_element_caracter(string, i):
    while(i+1<len(string)):
        i+=1
        if(string[i]!=' ' and string[i]!='\n'and string[i]!='\t'):
            return string[i], i
    return -1, -1

#Function that returns the next word (+ it's index)
def get_next_element_word(string, i, inclusive=False):
    while(i+1<len(string)):
        i+=1
        if(string[i]!=' ' and string[i]!='\n'):
            start, end=i-int(inclusive), i
            while(end<len(string)):
                if(string[end]==' ' or string[end]=='\n'):
                    return string[start:end], start
                end+=1
            return string[start:len(string)], start
    return -1, -1

#Get the end of a curly declaration +1
#We add the +1 to simplify later on when we use string[start:end]
#End refering to the value given by this function
def extract_curly(string, start):
    #Since we can never have "{{" in a workflow
    #We add this just so the function is more robust
    if(string[start]=='{'):
        start+=1
    count_curly = 1
    end = start
    work= string
    while(count_curly != 0):
        try:
            if(work[end] == "{"):
                count_curly += 1
            elif(work[end] == "}"):
                count_curly -= 1
            end += 1
        except Exception as e:
            print_in_red( f"In extract_curly out of range at index {end} and the curly count was at {count_curly}" )
            print_in_red( f"Started looking at : {string[start-20: start]}" )
            raise e
    return end
 
#Returns the string corresponding to the next line + start and end index
def get_next_line(string, i):
    start, end= i, i+1
    reading=False
    while(end<len(string)):
        if(not reading and (string[end]==' ' or string[end]=='\n')):
            None
        elif(not reading and (string[end]!=' ' and string[end]!='\n')):
            start=end
            reading=True
        elif(reading and string[end]=='\n'):
            return string[start:end].strip(), start, end-1
        end+=1
    return string[start:end].strip(), start, end-1

#Function that returns the condition of the first if in the string 
def extract_condition_2(string):
    pattern= r'if *\(([^\n]*)\)'
    for match in re.finditer(pattern, string):
        return match.group(1)

#Function that returns of the next curly opening 
#check_string allows the user to ignore the curlies in string such as 'some_adresse/text{1,2}.txt'
def get_index_next_curly(string, i, check_string=False):
    in_string=False
    while(i<len(string)):
        if(not check_string):
            if(string[i]=='{'):
                return i
        else:
            if((string[i]=="'" or string[i]=='"') and not in_string):
                in_string=True
            elif ((string[i]=="'" or string[i]=='"') and in_string):
                in_string= False
            elif(string[i]=='{' and not in_string):
                return i
        i+=1
    print_in_red( f"In get_index_next_curly a curly (open) was excepted but never found" )
    raise Exception("Curly never opened!!!")

#Same as get_index_next_curly but with closing curly
def get_index_next_curly_close(string, i, check_string=False):
    in_string=False
    while(i<len(string)):
        if(not check_string):
            if(string[i]=='}'):
                return i
        if(check_string):
            if((string[i]=="'" or string[i]=='"') and not in_string):
                in_string=True
            elif ((string[i]=="'" or string[i]=='"') and in_string):
                in_string= False
            elif(string[i]=='}' and not in_string):
                return i
        i+=1
    print_in_red( f"In get_index_next_curly_close a curly (close) was excepted but never found" )
    raise Exception("Curly never closed!!!")

#Function that links the different conditions together with an '&&'
#There is also a negative mode that sets the condition to negatives
def link_conditions(conditions, negative=False):
    temp=''
    if(len(conditions)==0):
        return temp
    elif(len(conditions)==1):
         negative*'!('+conditions[0]+negative*')'
    for i in range(len(conditions)-1):
        temp+= negative*'!('+conditions[i]+negative*')'+' && '
    temp+= negative*'!('+conditions[-1]+negative*')'
    return temp

#Function that adds spaces inbetween ifs and elses and the parenthesis or curly 
#And returns the modified string
def add_spaces(string):
    tab_replace=[]
    #============================
    # if(c) { => if (c) {
    #============================
    pattern = r'(if)(\([^\n]+\))\s+{'
    for match in re.finditer(pattern, string):
        start, end= match.span(0)[0], match.span(0)[1]
        start_if, end_if= match.span(1)[0], match.span(1)[1]
        new= string[start:end_if]+' '+string[end_if:end]
        tab_replace.append([match.group(0), new])
    
    #============================
    # if (c){ => if (c) {
    #============================
    pattern = r'(if) +(\([^\n]+\)){'
    for match in re.finditer(pattern, string):
        start, end= match.span(0)[0], match.span(0)[1]
        start_condition, end_conditon= match.span(2)[0], match.span(2)[1]
        new= string[start:end_conditon]+' '+string[end_conditon:end]
        tab_replace.append([match.group(0), new])
    #============================
    # if(c){ => if (c) {
    #============================
    pattern = r'(if)(\([^\n]+\)){'
    for match in re.finditer(pattern, string):
        start, end= match.span(0)[0], match.span(0)[1]
        start_if, end_if= match.span(1)[0], match.span(1)[1]
        start_condition, end_conditon= match.span(2)[0], match.span(2)[1]
        new= string[start:end_if]+' '+string[start_condition:end_conditon]+' '+string[end_conditon:end]
        tab_replace.append([match.group(0), new])

    #============================
    # simple else
    #============================
    pattern = r'[^\w](else)[^\w]'
    for match in re.finditer(pattern, string):
        start, end= match.span(0)[0], match.span(0)[1]
        start_else, end_else= match.span(1)[0], match.span(1)[1]
        new= string[start:start_else]+' '+string[start_else:end_else]+' '+string[end_else:end]
        tab_replace.append([match.group(0), new])
    
    for r in tab_replace:
        string= string.replace(r[0], r[1], 1)
    return string


#TODO add comments to this function
#Supposing that all the ifs and elses have curlies and the start is the begining of the if we want to analyse
#Supposing the spaces have also been added thanks to add_spaces
#tabs are references 
def format_if_recursif_3(string, start, end, conditions, last_conditon, new_string):
    #Gettig the if or else
    next= get_next_element_word(string, start, True)
    #in the case of else, we check if it's just a simple else or else if 
    the_word_after= get_next_element_word(string, next[1]+len(next[0]))
    
    word=next[0].strip()
    word_after= the_word_after[0].strip()

    i=get_index_next_curly(string, start)+1#Cause we don't want it to count => we don't want the curly as the orgin(the element just after it)
    condition=[]
    case_elif=False
    #In the case of of the word being if
    if(word=='if'):
        condition= [extract_condition_2(string[start:])]
        conditions+=condition
        
    #In the case of the word being by else
    elif(word=='else' and word_after!='if'):
        condition= [link_conditions(last_conditon, True)]
        conditions+=condition

    #In the case of the word being by else if
    elif(word=='else' and word_after=='if'):
        elif_condition= extract_condition_2(string[start:])
        condition= [elif_condition] + last_conditon
        case_elif=True
    else:
        raise Exception("Something went wrong! I don't know what i'm looking at: {}".format(word))
    

    curly_count=1
    #BAsically we declare this as an empty=> cause for the original if it will be empty=> 
    #it doesn't matter. And after that for the elses it will have a value 
    temp_condition=[]
    while(True):
        
        if(get_next_element_caracter(string, i)[0]=='{'):
            curly_count+=1
        elif(get_next_element_caracter(string, i)[0]=='}'):
            curly_count-= 1
        if(curly_count==0):
            break
        
        next_word=get_next_element_word(string, i)
        
        if(next_word[0]=='if' or next_word[0]=='else'):
            index_next_curly= get_index_next_curly(string, next_word[1])
            end= extract_curly(string, index_next_curly+1)
            temp_condition, new_string, temp= format_if_recursif_3(string, next_word[1], end, conditions.copy(), temp_condition, new_string)
            i=end
            
            
        else:
            next_line = get_next_line(string, i)
            line= next_line[0]
            i=next_line[2]
            if(not case_elif):
                condition_to_print=link_conditions(conditions)
            else:
                if(len(conditions)==0):
                    condition_to_print=elif_condition+' && '+ link_conditions(last_conditon, True)
                else:
                    condition_to_print=link_conditions(conditions)+' && '+elif_condition+' && '+ link_conditions(last_conditon, True)
                
            new_string+='<< {} ;; {} >>\n'.format(line, condition_to_print)
    return condition, new_string, get_index_next_curly_close(string, i)+1
    
    
#TODO => add comments
#Function that adds the curly to the ifs and elses one line
def add_curly(string):
    #We add this just to avoid some errors since we are looking at the '\n' => we remove the added '\n' at the end
    string+='\n'
    #Since we are using next_word and second_word we have to add a space inbetween the if and the condition, to be able to defferiante the 2
    #=======================
    #if(c) => if (c)
    #=======================
    pattern= r'if(\()'
    tab_replace=[]
    for match in re.finditer(pattern, string):
        start, end= match.span(0)[0], match.span(0)[1]
        start_condition, end_condition= match.span(1)[0], match.span(1)[1]
        new= string[start:start_condition]+' '+string[start_condition:end]
        tab_replace.append([match.group(0), new])
    for r in tab_replace:
        string= string.replace(r[0], r[1], 1)
    
    def extract_para(string, start):
        count_curly = 1
        end = start
        work= string
        while(count_curly != 0):
            if(work[end] == "("):
                count_curly += 1
            elif(work[end] == ")"):
                count_curly -= 1
            end += 1
        return end

    pattern_global= r'((if|else +if) *\([^\n]*\)|else)\s*[^\w]*'
    pattern_precise=r'((if|else +if) *\([^\n]*\)|else)\s*{[^\w]*'
    tab_pattern= [m.start(0) for m in re.finditer(pattern_global, string)]
    tab_curly= [m.start(0) for m in re.finditer(pattern_precise, string)]
    new_string=string
    #print(len(tab_curly))
    #print(len(tab_pattern))
    for t in tab_curly:
        tab_pattern.remove(t)
    #print(tab_pattern)
    for i in tab_pattern:
        first_word, first_index= get_next_element_word(string, i-1)
        #print(first_index==i)
        #print(first_word, string[first_index:first_index+len(first_word)])
        second_word, second_index= get_next_element_word(string, first_index+len(first_word))
        #print(second_word, string[second_index:second_index+len(second_word)])
        #print(first_word, second_word)
        if(first_word=='if'):
            next_caracter, next_index= get_next_element_caracter(string, first_index+len(first_word))
            end= extract_para(string, next_index+1)
            next_caracter, next_index= get_next_element_caracter(string, end)
            while(string[next_index]!='\n'):
                next_index+=1
            replacement= string[first_index:end]+' { \n '+string[end:next_index]+' \n}'
            new_string= new_string.replace(string[first_index:next_index], replacement)
            #print(string)
            #print('if')
        elif(first_word=='else' and second_word!='if'):
            next_caracter, next_index= get_next_element_caracter(string, first_index+len(first_word))
            #print(next_caracter)
            while(string[next_index]!='\n'):
                next_index+=1
            replacement= string[first_index:first_index+len(first_word)]+' { \n '+string[first_index+len(first_word):next_index]+' \n}'
            new_string= new_string.replace(string[first_index:next_index], replacement)
            #print("else")
        elif(first_word=='else' and second_word=='if'):
            next_caracter, next_index= get_next_element_caracter(string, second_index+len(second_word))
            end= extract_para(string, next_index+1)
            next_caracter, next_index= get_next_element_caracter(string, end)
            while(string[next_index]!='\n'):
                next_index+=1
            replacement= string[first_index:end]+' { \n '+string[end:next_index]+' \n }'
            new_string= new_string.replace(string[first_index:next_index], replacement)
    #Removing the added '\n' at the beggining 
    return new_string[:-1]


def format_conditions(string):
    """string= format_channels(string)
    string= put_on_one_line(string)
    string= add_spaces(string)
    string= add_curly(string)"""
    #print(string)

    #Start by removing the strings things "..." to remove any ambiguity
    strings=[]
    index_replace=0 
    pattern_small=r'\'.*\'|\".*\"'
    for match in re.finditer(pattern_small, string): 
        start= match.span()[0]
        end= match.span()[1]
        strings.append([string[start:end], "string_{}".format(index_replace)])
        index_replace+=1
        #string=string[:start]+create_empty(string, start, end)+string[end:]
    for s in strings:
        string= string.replace(s[0], s[1])

    i=0
    format=[]
    new_string=""
    start, fin=0, 0
    while(True):
        
        if(i>=len(string)):
            fin=i-1
            new_string+=string[start:fin]
            break

        first_word, index_next_word= get_next_element_word(string, i, True)
        if(first_word==-1):
            #print('made it here1')
            fin=i
            new_string+=string[start:fin]
            break

        the_word_after, index_word_after= get_next_element_word(string, index_next_word+len(first_word))
        if(the_word_after==-1):
            #print('made it here2')
            fin=index_next_word+len(first_word)
            new_string+=string[start:fin]
            break

        first_word, the_word_after= first_word.strip(), the_word_after.strip()
        #print(first_word, the_word_after)
        

        if(first_word=='if'):
            #print('if!!!')
            fin=index_next_word
            new_string+=string[start:fin]
            format= format_if_recursif_3(string, i, len(string), [], [], '')
            end=format[2]
            #string= string[:i]+format[1]+string[end:]
            new_string+=format[1]
            i=end
            start=i
        elif(first_word=='else' and the_word_after!='if'):
            #print(format[0].copy())
            #print('else!!!')
            format= format_if_recursif_3(string, i, len(string), [], format[0].copy(), '')
            end=format[2]
            #string= string[:i]+format[1]+string[end:]
            new_string+=format[1]
            i=end
            start=i
        elif(first_word=='else' and the_word_after=='if'):
            #print(format[0])
            #print(format[0].copy())
            #print('else if!!!')
            format= format_if_recursif_3(string, i, len(string), [], format[0].copy(), '')
            end=format[2]
            #string= string[:i]+format[1]+string[end:]
            new_string+=format[1]
            i=end
            start=i
        else:
            i=index_next_word+len(first_word)
        #print(new_string)

    #Put the strings back
    #Start at the end of the list to replace in the big numbers first since we're replacing all the occurences 
    for i in range(len(strings)-1, -1, -1):
        #print(i)
        s= strings[i]
        #print('HERE')
        #print(s[1], s[0])
        new_string= new_string.replace(s[1], s[0])

    return new_string


if __name__ == "__main__":
    test="""
        if(clemence){
            yo
        }else{
            no yo
        }
        """
    #print(format_conditions(add_curly(add_spaces(test))))
    a=[1, 2,3, 4, 5, 6]
    print(check_containing(743, a))

