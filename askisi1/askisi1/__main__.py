import sys
from pathlib import Path
from data import Data

def main():
    first_test = Data("myTest1.txt")
    first_test.printTest()

if __name__ == "__main__":
    sys.exit(main())