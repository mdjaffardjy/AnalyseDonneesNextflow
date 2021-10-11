from workflow import *

if __name__ == "__main__":
    #Simple test which isn't very pretty
    #Right now we're supposing that the workflow script is just one doc and that it exists 
    adress= input("What's the adress of the workflow? ==> ")
    print("\n")
    f = open(adress,"r")
    lines = f.read()

    w1= Workflow(lines)
    w1.extractWorflow()
    w1.printProcessesName()
