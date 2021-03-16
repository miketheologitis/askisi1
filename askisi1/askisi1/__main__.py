import sys
from pathlib import Path
from testing import Test

def main():
    my_test = Test("sampleGraph2.txt")
    my_test.do_everything()

if __name__ == "__main__":
    sys.exit(main())