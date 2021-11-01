
from typeMain import * 

class TypeMainDSL2(TypeMain):
    def __init__(self, address):
        super().__init__(address)


    def initialise(self):
        self.initialise_basic_main()
        None

if __name__ == "__main__":
    print("I shoudn't be executed as a main")