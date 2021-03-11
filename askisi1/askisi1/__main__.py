import sys
from pathlib import Path
from data import Data

def main():
    #TODO: change name of first_test
    first_test = Data("myTest1.txt")
    
    first_test.parse_day_predictions() #rethink parse day predictions so we include the algorithm
    
    #first_test.print_test()
    first_test.print_test()
    ucs_prediction, prediction = first_test.make_prediction()
    for node in prediction:
        print(node, "->", end=" ")
    print()
    print("PREDICTED WEIGHT:", ucs_prediction)

if __name__ == "__main__":
    sys.exit(main())