import sys

def main(args=None):

    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    print("Hello world")

if __name__ == "__main__":
    sys.exit(main())