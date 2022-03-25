# Nextflow Analyzer
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022

import re

#Function that returns an empty string
def create_empty(string, start, end):
    empty=''
    for i in range(start, end):
        if(string[i]=='\n'):
            empty+='\n'
        else:
            empty+=' '
    return empty

class File:
    def __init__(self, address):
        self.address = address
        self.string = None
        #This attribute could be used to save the comments
        self.comments = []
        
    #Sets the string of the file to the attribute 
    def set_string(self):
        f = open(self.address,"r")
        self.string = f.read()
        f.close()

    #Method that prints the file string
    def print_file(self):
        print(self.string)

    #Method that returns the string
    def get_string(self):
        return self.string

    #Method that removes the comments from the file 
    #There are 2 ways to define comments:
    #   - one line comments "//comment"
    #   - multi lines comments "/*comment*/"
    def remove_comments(self):
        #Defining 2 lists for the strings and the script that are going extracted 
        #This is done since these cases can be ambiguous
        strings, scripts = [], []
        string= self.string

        #Removing script parts => the scripts that are in the processes
        #=======================
        in_script=False
        start, end=0, 0
        for i in range(0, len(string)-2):
            if(string[i]=='"' and string[i+1]=='"' and string[i+2]=='"' and not in_script):
                in_script=True
                start= i
            elif(string[i]=='"' and string[i+1]=='"' and string[i+2]=='"' and in_script):
                in_script=False
                end= i+2
                scripts.append([string[start:end], start, end])
        #=======================
        in_script=False
        start, end=0, 0
        for i in range(0, len(string)-2):
            if(string[i]=="'" and string[i+1]=="'" and string[i+2]=="'" and not in_script):
                in_script=True
                start= i
            elif(string[i]=="'" and string[i+1]=="'" and string[i+2]=="'" and in_script):
                in_script=False
                end= i+2
                scripts.append([string[start:end], start, end])
        #=======================
        for s in scripts:
            word, start, end=s[0], s[1], s[2]
            string= string=string[:start]+create_empty(string, start, end)+string[end:]



        #Removing the strings with ambiguities
        pattern_close = r'(\'.*(\*\/).*\'|\".*(\*\/).*\")'
        pattern_open = r'(\'.*(\/\*).*\'|\".*(\/\*).*\")'
        pattern_double = r'(\'.*(\/\/).*\'|\".*(\/\/).*\")'
        for pattern in [pattern_close, pattern_open, pattern_double]:
            for match in re.finditer(pattern, string): 
                start= match.span()[0]
                end= match.span()[1]
                strings.append([string[start:end], start, end])
                string=string[:start]+create_empty(string, start, end)+string[end:]
        

        def remove_big_comments(text):
            text= list(text)
            i=0
            in_comment=False
            while(i<len(text)-1):
                if( (not in_comment) and text[i]=='/' and text[i+1]=='*'):
                    in_comment = True
                    text[i], text[i+1] = ' ', ' '
                    i+=2
                elif(in_comment and text[i]=='*' and text[i+1]=='/' ):
                    in_comment = False
                    text[i], text[i+1] = ' ', ' '
                    i+=2
                elif(in_comment):
                    if(text[i]!='\n'):
                        text[i]= ' '
                    i+=1
                else:
                    i+=1
            return ''.join(text)
        string= remove_big_comments(string)

        #REMOVE COMMENTS //... without checking since there is no longer ambuity
        #-------------------------------------------------------------------------------------
        pattern =r'(\/\/[^\n]*)'
        for match in re.finditer(pattern, string): 
                start= match.span()[0]
                end= match.span()[1]
                string=string[:start]+create_empty(string, start, end)+string[end:]
        #-------------------------------------------------------------------------------------

        #PUT THE STRINGS BACK
        #-------------------------------------------------------------------------------------
        for s in strings:
            word, start, end=s[0], s[1], s[2]
            string=string[:start]+word+string[end:]
        for s in scripts:
            word, start, end=s[0], s[1], s[2]
            string=string[:start]+word+string[end:]
        #-------------------------------------------------------------------------------------
        
        self.string= string


    #Initialise the basic stuff for a file type
    def initialise_basic_file(self):
        self.set_string()
        self.remove_comments()





