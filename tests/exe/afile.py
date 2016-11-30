import bfile

def three():
    bfile.bar("this is not valid json")

def two():
    three()

def foo():
    two()
