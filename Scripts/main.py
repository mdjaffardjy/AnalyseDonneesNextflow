from workflow import *

if __name__ == "__main__":
    #Right now we're supposing that the address which is given is the "root" of the workflow project
    #The main.nf is situadted at the root
    #In the case of DSL2 all the nextflow files in that root (recursevely) will be analysed and the structure reconstructed
    address= input("What's the adress of the workflow? ==> ")
    print("\n")
    
    w1= Workflow(address)
    w1.initialise()
