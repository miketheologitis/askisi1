import sys
from pathlib import Path
from testing import Test

def main():
    my_test = Test("myTest1.txt")
    my_test.solution()

if __name__ == "__main__":
    sys.exit(main())