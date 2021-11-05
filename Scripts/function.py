

class Function:
    def __init__(self, function):
        #For now we are only defining the string and name atrributes
        #If we need to analyse functions later on, obsiously come here
        self.string = function
        self.name = None
        

    #Method that prints the string of the function
    def print_function(self):
        print(self.string)

    #Method that extracts the name of the function
    #We can't use regex for this in the case defining function in function=> it wouldn't know witch one to use,  so we have to do it 'by manuallly'
    def extract_name(self):
        p = "def"
        start= self.string.find(p)+ len(p)
        end= start
        while(self.string[end]!='('):
            end+=1
        word= self.string[start:(end)].strip()
        self.name= word

    #Method that prints the name of the function
    def print_name(self):
        print(self.name)

    #Method that returns the name of the function
    def get_name(self):
        return self.name

    #Method that returns the string of the function
    def get_string(self):
        return self.string


    #Initialise the basic stuff for a function type
    def initialise_function(self):
        self.extract_name()
        #Do stuff

#=================
#IF USED AS A MAIN
#=================
if __name__ == "__main__":
    print("I shoudn't be executed as a main")


#TODO list:
#   - Comment the code
#   - do extract name!