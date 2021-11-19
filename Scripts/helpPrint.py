from process import *

"""
Process Informations
"""
def printInformations(resProcess):
    print("----NAME PROCESS----")
    resProcess.printName()
    print("  ")
    print("----DIRECTIVES----")
    resProcess.printDirectives()
    print("  ")
    print("----INPUTS----")
    resProcess.printInput()
    print("  ")
    print("----OUTPUTS----")
    resProcess.printOutput()
    print("  ")
    print("----WHEN----")
    resProcess.printWhen()
    print("  ")
    print("----SCRIPT----")
    resProcess.printScript()
    print("   ")
    print("----STUB----")
    resProcess.printStub()
    print("  ")

def printNameInWorkflow(resProcess):
    print("Inputs - Source channel : ", resProcess.input.list_words_workflow)
    print("Outputs -  Target channel : ",resProcess.output.list_output)
    print("  ")

  
def printLanguage(resProcess):
    print("Language Script:", resProcess.script.getLanguage())
    if resProcess.stub != None:
        print("Language Stub:", resProcess.stub.getLanguage())
    print("  ")


def printQualifier(resProcess):
    print("Qualifier of directive : ", resProcess.directive.getQualifier())
    print("Qualifier of input : ",resProcess.input.getQualifier())
    print("Qualifier of output : ",resProcess.output.getQualifier())
    print("  ")