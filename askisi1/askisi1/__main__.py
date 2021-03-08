import sys
from pathlib import Path
from initializeProblem import*

def main(args=None):

    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    #https://stackoverflow.com/questions/40416072/reading-file-using-relative-path-in-python-project
    path = Path(__file__).parent  / "../data/myTest1.txt"
    file = open(path, "r")

    source = getSource(file)
    destination = getDestination(file)

    #https://codereview.stackexchange.com/questions/163414/adjacency-list-graph-representation-on-python

    getGraphAndWeights(file)
    file.close()



if __name__ == "__main__":
    sys.exit(main())