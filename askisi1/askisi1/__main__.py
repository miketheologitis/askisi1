import sys
from pathlib import Path
from testing import Test

def main():
    t = Test("sampleGraph1.txt")
    t.print_test()
    
if __name__ == "__main__":
    sys.exit(main())