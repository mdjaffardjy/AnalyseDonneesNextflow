import re

from process_test import *

class File:
    def __init__(self, address):
        self.address = address
        self.string = None
        self.name = None
        
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

    #Method that removes all the comments from the string
    #The rules definied for the comments follows the ones definied by nextflow/ groovy so '//' or '/*...*/'
    def remove_comments(self):
        in_comment_one_line, in_big_comment= False, False
        new_string=""
        i=0
        while(i < len(self.string)-1):

            #In case we see the one ligne comment marker '//'
            if(self.string[i:i+2]=="//" and not in_comment_one_line and not in_big_comment):
                in_comment_one_line= True
                new_string+='\n'
                i+=1
            #In case we're in comment one line and we change line
            elif(self.string[i:i+1]=="\n" and in_comment_one_line):
                in_comment_one_line= False

            #In case we see '/*' to open the 'big' comment
            elif(self.string[i:i+2]=="/*" and not in_big_comment and not in_comment_one_line):
                in_big_comment= True
                i+=1
            #In case we see '*/' to close the 'big' comment
            elif(self.string[i:i+2]=="*/" and in_big_comment):
                in_big_comment= False
                i+=1

            #if we're not in a comment we write the rest of the string
            elif(not in_comment_one_line and not in_big_comment):
                new_string+= self.string[i]
                #Basically the last letter won't be written if we don't write this
                if(i==len(self.string)-2):
                    new_string+= self.string[i+1]
            i+=1

        self.string= new_string

    #Using REGEX
    def remove_comments_2(self):
        pattern_one_line= r'(\/\/[^ \n]*)'
        pattern_big= r'(\/\*(\w|\W)*\*\/)'
        temp=self.string

        for match in re.finditer(pattern_big, temp):
            temp = temp.replace(temp[match.span()[0]:match.span()[1]], '')

        for match in re.finditer(pattern_one_line, temp):
            temp = temp.replace(temp[match.span()[0]:match.span()[1]], '')
        
        self.string=temp

    def initialise_basic_file(self):
        #Do Stuff
        self.set_string()
        #Right now we're not removing comments, it creates a problem with eager for example
        #when extracting the processes
        #Don't know why right now
        #self.remove_comments()

if __name__ == "__main__":
    """f= File('/home/george/Bureau/TER/test.txt')
    f.initialise_basic_file()
    f.print_file()#"""
    print("I shoudn't be executed as a main")



#OLD TODO List:
#   - re-work the extract processes method since it doesn't work very well (small task)
#   - write the method that determines which 'type' of file we are dealing with (medium task)
#   - for each type write the specifities that makes it them (big task)
#
#   - think about how to deal with channels and functions if we have to deal with them (big task)