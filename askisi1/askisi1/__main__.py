import sys
from pathlib import Path
from testing import Test

def main():
    first_test = Test("myTest1.txt")
    first_test.print_test()

if __name__ == "__main__":
    sys.exit(main())