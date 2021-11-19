import re

from process_test import *

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
        self.name = None
        self.comments= []
        
    #Sets the string of the file to the attribute 
    def set_string(self):
        f = open(self.address,"r")
        self.string = f.read()
        f.close()

    #Method that prints the file string
    def print_file(self):
        print(self.string)

    #Method returns the 
    def get_string(self):
        return self.string


    #TODO: Save COMMENTS
    #Method that removes all the comments from the string
    #The rules definied for the comments follows the ones definied by nextflow/ groovy so '//' or '/*...*/'
    def remove_comments(self):
        strings=[]
        string= self.string
        
        #FIRST START BY REMOVING THE STRING WITH '//' in them
        #-------------------------------------------------------------------------------------
        pattern= r'(\'.*\/\/[^\n]*\'|\".*\/\/[^\n]*\")'
        for match in re.finditer(pattern, string): 
                start= match.span()[0]
                end= match.span()[1]
                strings.append([string[start:end], start, end])
                string=string[:start]+create_empty(string, start, end)+string[end:]
        #-------------------------------------------------------------------------------------
        
        #WE REMOVE THE COMMENTS //..*/....
        #-------------------------------------------------------------------------------------
        pattern =r'//.*\*\/.*'
        for match in re.finditer(pattern, string): 
                start= match.span()[0]
                end= match.span()[1]
                string=string[:start]+create_empty(string, start, end)+string[end:]
        #-------------------------------------------------------------------------------------

    
        #REMOVE COMMENTS /*..*/ without ambuity
        #-------------------------------------------------------------------------------------
        pattern= r'/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'
        tab=[]
        for match in re.finditer(pattern, string): 
                start= match.span()[0]
                end= match.span()[1]
                tab.append([start, end])
        
        for m in tab:
            start=m[0]
            end= m[1]
            if(string[start:end].count('"')==0 and string[start:end].count("'")==0):
                #print(string[start:end])
                string=string[:start]+create_empty(string, start, end)+string[end:]
        #-------------------------------------------------------------------------------------

        #REMOVE COMMENTS //... without checking since there is no longer ambuity
        #-------------------------------------------------------------------------------------
        pattern =r'(\/\/[^\n]*)'
        for match in re.finditer(pattern, string): 
                start= match.span()[0]
                end= match.span()[1]
                string=string[:start]+create_empty(string, start, end)+string[end:]
        #-------------------------------------------------------------------------------------
    
        #REMOVE THE REMAINAING STRINGS
        #-------------------------------------------------------------------------------------
        #Start with 'big' string
        """pattern_big= r'\"\"\"([^\"]|[\r\n]|(\*+([^\"\"\"]|[\r\n])))*\"\"\"|\'\'\'([^\']|[\r\n]|(\*+([^\'\'\']|[\r\n])))*\'\'\''
        tab=[]
        for match in re.finditer(pattern_big, string): 
                start= match.span()[0]
                end= match.span()[1]
                tab.append([start, end])
                strings.append([string[start:end], start, end])
                string=string[:start]+create_empty(string, start, end)+string[end:]"""
                
        #We go on to the small comments
        pattern_small=r'\'.*\'|\".*\"'
        tab=[]
        for match in re.finditer(pattern_small, string): 
                start= match.span()[0]
                end= match.span()[1]
                strings.append([string[start:end], start, end])
                string=string[:start]+create_empty(string, start, end)+string[end:]
                
        #-------------------------------------------------------------------------------------
        

        #REMOVE THE REMAINAING COMMENTS
        #-------------------------------------------------------------------------------------
        pattern= r'/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'
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
        #-------------------------------------------------------------------------------------
        #print(string)
        self.string= string


    #Initialise the basic stuff for a file type
    def initialise_basic_file(self):
        #Do Stuff
        self.set_string()
        self.remove_comments()


#=================
#IF USED AS A MAIN
#=================
if __name__ == "__main__":
    """f= File('/home/george/Bureau/TER/test.txt')
    f.initialise_basic_file()
    f.print_file()#"""
    print("I shoudn't be executed as a main")



#TODO List:
#   - Remove the old versions of remove_comments and clean up the final working version
