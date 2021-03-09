import sys
from pathlib import Path
from data import Data

def main():
    #TODO: change name of first_test
    first_test = Data("myTest1.txt")
    first_test.printTest()

if __name__ == "__main__":
    sys.exit(main())