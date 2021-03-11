from pathlib import Path
from collections import defaultdict
from decimal import Decimal
from algorithms import ucs

"""
weights is a dictionary with key = (Node1, Node2), value = weight, but 
the idea about weights is for example A->B weight will get a specific value (actually the last value stored from a road to A,B or B,A so that
weights[A,B] = weights[B,A]) and even though this might NOT be the lowest weight we dont care. This is because weights will get "fixed" by the 
predictions of each day, so that FOR EXAMPLE if a Road1 (from A->B or B->A) is low traffic and weightOf(Road1)<weights[A,B] THEN 
weights[A,B] = weightOf(Road1). In few words we will fix the weight of A->B and B->A when we make our predictions and we will TRANSFORM the multigraph
to single graph with SAFETY!
We will use road dictionary to use the predictions and fix our weights. Example: weight[road["Road20"]] = ... , if it is necessary
"""
#https://cyluun.github.io/blog/uninformed-search-algorithms-in-python
#https://www.youtube.com/watch?v=dRMvK76xQJI ucs algorithm
class Data:
    def __init__(self, filename):
        #https://stackoverflow.com/questions/40416072/reading-file-using-relative-path-in-python-project
        self.file = open(Path(__file__).parent  / ("../data/"+filename), "r")

        self.source = ""
        self.destination = ""
        self.graph = defaultdict(set) #BIDIRECTIONAL GRAPH with dictionary with key=Node , value={AdjacentNode1, AdjacentNode2, ...}
        self.weight = {} #dictionary with key=(Node1, Node2), value=weight
        self.road = {} #dictionary with key="RoadName1" , value=(Node20,Node30)
        
        self.parse_source()
        self.parse_destination()
        self.parse_roads()
        self.skip_line()
        
    
    def skip_line(self):
        self.file.readline()

    def parse_source(self):
        self.source = self.file.readline().replace("<Source>", "").replace("</Source>", "").strip()
    
    def parse_destination(self):
        self.destination = self.file.readline().replace("<Destination>", "").replace("</Destination>", "").strip()

    #https://codereview.stackexchange.com/questions/163414/adjacency-list-graph-representation-on-python
    def parse_roads(self):
        self.skip_line()
        line = self.file.readline().strip()
        while(line != "</Roads>"):
            tmp = line.replace(" ", "").split(";")
            #create bidirectional graph (Note: sets cant have duplicate values so we are good)
            self.graph[tmp[1]].add(tmp[2])
            self.graph[tmp[2]].add(tmp[1])

            #create weights so that weight[Node1, Node2] = weight[Node2, Node1] and we will fix weights from predictions
            self.weight[tmp[1],tmp[2]] = -1
            self.weight[tmp[2],tmp[1]] = -1

            #create road so that road["RoadName"] = (Node20, Node30, normal weight)
            self.road[tmp[0]] = tmp[1],tmp[2],int(tmp[3])
            line = self.file.readline().strip()

    def parse_day_predictions(self):
        self.skip_line()
        line = self.file.readline().strip()

        while(line != "</Day>"):
            #self.reset_weight()
            tmp = line.replace(" ", "").split(";")
        
            #fix the weight
            nodes = self.road[tmp[0]][0:2]  #means nodes = road["Road1"][0:2] = (Node1, Node2)
            normal_weight = self.road[tmp[0]][2] #means normal_weight = road["Road1"][3] = weight

            #here we check whether the new weight depending on heavy, low or normal should be placed
            #in our weight dictionary. The weight dictionary is initialized with -1 weights
            #so if our new_weight is < the old weight (or the old wieght is -1) then replace 
            if(tmp[1]=="low"):
                new_weight = self.weight_in_low_traffic(normal_weight)
                if(self.weight[nodes] > new_weight or self.weight[nodes] == -1):
                    self.weight[nodes] = new_weight
                    self.weight[nodes[1],nodes[0]] = new_weight
            elif(tmp[1]=="heavy"):
                new_weight = self.weight_in_heavy_traffic(normal_weight)
                if(self.weight[nodes] > new_weight or self.weight[nodes] == -1):
                    self.weight[nodes] = new_weight
                    self.weight[nodes[1],nodes[0]] = new_weight
            else:
                if(self.weight[nodes] > normal_weight or self.weight[nodes] == -1):
                    self.weight[nodes] = normal_weight
                    self.weight[nodes[1],nodes[0]] = normal_weight
            line = self.file.readline().strip()
    
    def weight_in_heavy_traffic(self, number): 
        return float(Decimal(number)*Decimal(1.25))
    def weight_in_low_traffic(self, number): 
        return float(Decimal(number)*Decimal(0.9))
    
    def reset_weight(self):
        for key in self.weight:
            self.weight[key] = -1
    
    def make_prediction(self):
        return ucs(self.graph, self.weight, self.source, self.destination)
    
    def print_path_cost(self, lst):
        cost = 0
        for i in range(len(lst)-1):
            cost += self.weight[lst[i],lst[i+1]]
        return cost
        
    def print_test(self):
        self.print_graph()
        self.print_weight()
        self.print_road()
    def print_graph(self):
        print()
        print("________GRAPH_________")
        for node in self.graph:
            print(node, ":", self.graph[node])
        print()
    def print_weight(self):
        print()
        print("________WEIGHT_________")
        for node1, node2 in self.weight:
            print((node1,node2) , ":", self.weight[node1,node2])
        print()
    def print_road(self):
        print()    
        print("________ROAD_________")
        for r in self.road:
            print(r , ":", self.road[r])
        print()