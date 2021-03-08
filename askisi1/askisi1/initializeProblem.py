from html.parser import HTMLParser

def getSource(file):
    return file.readline().replace("<Source>", "").replace("</Source>", "").strip()

def getDestination(file):
    return file.readline().replace("<Destination>", "").replace("</Destination>", "").strip()

def getGraphAndWeights(file):
    print(file.readline())
    line = file.readline().strip()
    while(line != "</Roads>"):
        lst = line.replace(" ", "").split(";")
        line = file.readline().strip()
        print(line)
