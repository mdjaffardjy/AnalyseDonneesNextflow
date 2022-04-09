class When:
    def __init__(self, strWhen):
            self.when_string = strWhen

    def printWhen(self):
        print(self.when_string)

    def getWhen(self):
        return self.when_string
            
if __name__ == "__main__":
    print("I shouldn't be executed as a main")
