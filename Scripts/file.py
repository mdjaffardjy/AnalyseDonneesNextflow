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
    #Doesn't seem to work to well, i think it's a problem with '/* */'
    def remove_comments_2(self):
        #We ignore the '//' used in an internet address
        pattern_one_line= r'([^https:]\/\/[^\n]*)'
        pattern_big= r'(\/\*(\w|\W)*\*\/)'
        temp=self.string

        def create_empty(start, end):
            empty=''
            for i in range(start, end):
                if(temp[i]=='\n'):
                    empty+='\n'
                else:
                    empty+=' '
            return empty

        for match in re.finditer(pattern_one_line, temp): 
            temp = temp.replace(temp[match.span()[0]:match.span()[1]], create_empty(match.span()[0], match.span()[1]))

        def change_letter(string, letter, index):  # note string is actually a bad name for a variable
            return string[:index] + letter + string[index+1:]

        in_big_comment= False
        i=0
        while(i < len(temp)-1):
            #In case we see '/*' to open the 'big' comment
            if(temp[i:i+2]=="/*" and not in_big_comment):
                in_big_comment= True
                temp= change_letter(temp, ' ', i)
                temp= change_letter(temp, ' ', i+1)
                i+=1
            #In case we see '*/' to close the 'big' comment
            elif(temp[i:i+2]=="*/" and in_big_comment):
                in_big_comment= False
                temp= change_letter(temp, ' ', i)
                temp= change_letter(temp, ' ', i+1)
                i+=1
            #In case we're in a big comment
            elif(in_big_comment):
                temp= change_letter(temp, ' ', i)     
            i+=1        
        self.string=temp
    
    def remove_comments_one_line(self):
        #We ignore the '//' used in an internet address
        pattern_one_line= r'([^https:]\/\/[^\n]*)'
        temp=self.string

        def create_empty(start, end):
            empty=''
            for i in range(start, end):
                if(temp[i]=='\n'):
                    empty+='\n'
                else:
                    empty+=' '
            return empty

        for match in re.finditer(pattern_one_line, temp): 
            temp = temp.replace(temp[match.span()[0]:match.span()[1]], create_empty(match.span()[0], match.span()[1]))

        self.string = temp
    

    #Removes the majority of the comments still a bit buggy but it works well enough
    #TODO maybe do a mix of the regex one and this one => best of both worlds
    #You can't use replace!! for example imagine we want to remove '/////' form the string but before that there is '/////////' well it will remove '/////' in '/////////'
    #So you definitely need to use the indexes 
    def remove_comments_3(self):
        in_comment_one_line, in_big_comment, in_string_single, in_string_double= False, False, False, False
        comments=[]
        i=0
        start, end= 0, 0
        while(i < len(self.string)-1):

            #If we're defining a string
            if(self.string[i]=="'" and not in_string_single and not in_string_double and not in_big_comment):
                in_string_single = True
            #If we're defining a string
            elif(self.string[i]=='"' and not in_string_double and not in_string_single and not in_big_comment):
                in_string_double = True
            #If we're getting out of the string
            elif(self.string[i]=="'" and in_string_single and not in_string_double):
                in_string_single = False
            #If we're getting out of the string
            elif(self.string[i]=='"' and in_string_double and not in_string_single):
                in_string_double = False

            #In case we see the one ligne comment marker '//'
            elif(self.string[i:i+2]=="//" and not in_comment_one_line and not in_big_comment):
                in_comment_one_line= True
                start = i
                i+=1
            #In case we're in comment one line and we change line
            elif(self.string[i:i+1]=="\n" and in_comment_one_line):
                end= i+1
                in_comment_one_line= False
                comments.append(self.string[start:end])

            #In case we see '/*' to open the 'big' comment
            elif(self.string[i:i+2]=="/*" and not in_big_comment and not in_comment_one_line and not in_string_double and not in_string_single):
                in_big_comment= True
                start = i
                i+=1
            #In case we see '*/' to close the 'big' comment
            elif(self.string[i:i+2]=="*/" and in_big_comment and not in_comment_one_line and not in_string_double and not in_string_single):
                in_big_comment= False
                i+=1
                end= i
                comments.append(self.string[start:end+1])
            
            i+=1

        for i in range(len(comments)):
            self.string= self.string.replace(comments[i], '')

    
    #STILL ONE BUG
    def remove_comments_4(self):
        def create_empty(start, end, temp):
            empty=''
            for i in range(start, end):
                if(temp[i]=='\n'):
                    empty+='\n'
                else:
                    empty+=' '
            return empty
        
        in_comment_one_line, in_big_comment, in_string_single, in_string_double= False, False, False, False
        comments=[]
        i=0
        start, end= 0, 0
        while(i < len(self.string)-1):

            #If we're defining a string
            if(self.string[i]=="'" and not in_string_single and not in_string_double and not in_big_comment):
                in_string_single = True
            #If we're defining a string
            elif(self.string[i]=='"' and not in_string_double and not in_string_single and not in_big_comment):
                in_string_double = True
            #If we're getting out of the string
            elif(self.string[i]=="'" and in_string_single and not in_string_double):
                in_string_single = False
            #If we're getting out of the string
            elif(self.string[i]=='"' and in_string_double and not in_string_single):
                in_string_double = False

            #In case we see the one ligne comment marker '//'
            elif(self.string[i:i+2]=="//" and not in_comment_one_line and not in_big_comment):
                in_comment_one_line= True
                start = i
                i+=1
            #In case we're in comment one line and we change line
            elif(self.string[i:i+1]=="\n" and in_comment_one_line):
                end= i+1
                in_comment_one_line= False
                comments.append([start, end])

            #In case we see '/*' to open the 'big' comment
            elif(self.string[i:i+2]=="/*" and not in_big_comment and not in_comment_one_line and not in_string_double and not in_string_single):
                in_big_comment= True
                start = i
                i+=1
            #In case we see '*/' to close the 'big' comment
            elif(self.string[i:i+2]=="*/" and in_big_comment and not in_comment_one_line and not in_string_double and not in_string_single):
                in_big_comment= False
                i+=1
                end= i
                comments.append([start, end+1])
            
            i+=1

        for i in range(len(comments)):

            temp= list(self.string)
            start, end= comments[i][0], comments[i][1]
            temp[start:end]= create_empty(start, end, self.string)
            self.string= ''.join(temp)


    #Initialise the basic stuff for a file type
    def initialise_basic_file(self):
        #Do Stuff
        self.set_string()

        #Right now we're not removing comments, it creates a problem with eager for example
        #when extracting the processes
        #Don't know why right now
        #self.remove_comments_2()
        #self.remove_comments_one_line()
        self.remove_comments_4()

#=================
#IF USED AS A MAIN
#=================
if __name__ == "__main__":
    """f= File('/home/george/Bureau/TER/test.txt')
    f.initialise_basic_file()
    f.print_file()#"""
    print("I shoudn't be executed as a main")



#TODO List:
#   - Fix remove comments
#   - Remove the old version of the method and clean up the final working version
