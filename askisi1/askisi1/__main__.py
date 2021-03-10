import sys
from pathlib import Path
from data import Data

def main():
    #TODO: change name of first_test
    first_test = Data("sampleGraph1.txt")
    first_test.print_test()

if __name__ == "__main__":
    sys.exit(main())