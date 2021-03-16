from pathlib import Path
from collections import defaultdict
from decimal import Decimal
from algorithms import ucs, dijkstra_create_heuristic, ida_star
import random


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
        self.file_traff = open(Path(__file__).parent  / ("../data/"+filename), "r") #file_predictions, file_pred is used to read the actual traffic

        self.source = ""
        self.destination = ""
        self.graph = defaultdict(set) #dictionary with key=Node , value={AdjacentNode1, AdjacentNode2, ...}
        self.weight = {} #dictionary with key=(Node1, Node2), value=weight
        self.weight_roads = {} #dictionary with the chosen road connecting two nodes each day (cheapest) weight_roads(NodeA, NodeB) = cheapest road
        self.road_info = {} #dictionary with key="RoadName1" , value=(Node20,Node30, normal weight)
        self.traffic_prediction = {} #predictions
        self.real_traffic = {} #actual daily traffic
        self.day = 1

        self.heuristic_help = {}
        self.heuristic = {}

        self.p1 = 0.6 #this is the chance of making the RIGHT prediction
        self.p2 = 0.2 #this is the chance of overestimaton of cost
        self.p3 = 0.2 #this is the chance of underestimation of cost
        
        self.parse_source()
        self.parse_destination()
        self.parse_roads()
        self.file.readline()
        
        self.init_heuristic()

        self.go_to_actual_traffic()
        
    def go_to_actual_traffic(self):
        while(self.file_traff.readline().strip() != "<ActualTrafficPerDay>"):
            pass

    def parse_source(self):
        self.source = self.file.readline().replace("<Source>", "").replace("</Source>", "").strip()
    
    def parse_destination(self):
        self.destination = self.file.readline().replace("<Destination>", "").replace("</Destination>", "").strip()
    
    def parse_actual_traffic(self):
        self.file_traff.readline()
        line = self.file_traff.readline().strip()
        while(line != "</Day>"):
            tmp = line.replace(" ", "").split(";")
            self.real_traffic[tmp[0]] = tmp[1]
            line = self.file_traff.readline().strip()
            
    #https://codereview.stackexchange.com/questions/163414/adjacency-list-graph-representation-on-python
    def parse_roads(self):
        self.file.readline()
        line = self.file.readline().strip()
        while(line != "</Roads>"):
            tmp = line.replace(" ", "").split(";")
            #(Note: sets cant have duplicate values so we are good)
            self.graph[tmp[1]].add(tmp[2])
            self.graph[tmp[2]].add(tmp[1])

            #create weights so that weight[Node1, Node2] = weight[Node2, Node1] and we will fix weights from predictions
            self.weight[tmp[1],tmp[2]] = None
            self.weight[tmp[2],tmp[1]] = None

            #create road weights so that weight_roads[Node1, Node2] = RoadA which is the chosen road each day connecting two nodes
            self.weight_roads[tmp[2],tmp[1]] = None
            self.weight_roads[tmp[1],tmp[2]] = None

            self.heuristic_help[tmp[2],tmp[1]] = None
            self.heuristic_help[tmp[1],tmp[2]] = None


            #create road so that road["RoadName"] = (Node20, Node30, normal weight)
            self.road_info[tmp[0]] = tmp[1],tmp[2],int(tmp[3])
            line = self.file.readline().strip()

    def parse_day_predictions(self):
        self.file.readline()
        line = self.file.readline().strip()

        while(line != "</Day>"):
            tmp = line.replace(" ", "").split(";")

            self.traffic_prediction[tmp[0]] = tmp[1]
            nodes = self.road_info[tmp[0]][0:2]  #means nodes = road_info["Road1"][0:2] = (Node1, Node2)
            new_weight = self.prediction_weight(tmp[1], tmp[0])

            #here we check whether the new weight depending on heavy, low or normal should be placed
            #in our weight dictionary. The weight dictionary is initialized with null weights
            #so if our new_weight is < the old weight (or the old wieght is null) then replace 
            #because we always want to keep the cheapest path from NodeA->NodeB regardless
            if(self.weight[nodes] == None or self.weight[nodes] > new_weight):
                #cheapest weight from nodeA to nodeB
                self.weight[nodes] = new_weight
                self.weight[nodes[1],nodes[0]] = new_weight
                #cheapest road from nodeA to nodeB
                self.weight_roads[nodes] = tmp[0]
                self.weight_roads[nodes[1],nodes[0]] = tmp[0]
            line = self.file.readline().strip()
            
    def prediction_weight(self, traffic, road): #return the new weight based on our propabilities p1,p2,p3
        rand = random.random() #random number between 0-1

        if (traffic == "low"):
            if(rand <= self.p1): #then choose our prediction
                return self.weight_in_low_traffic(self.road_info[road][2]) #road_info["Road1"][3] = normal weight, and we return low traffic weight
            elif(rand <= (self.p1+self.p2)): #p2 : overestimation of cost, so low -> low
                return self.weight_in_low_traffic(self.road_info[road][2]) #we return low traffic weight
            else: #p3 : underestimation of cost
                return self.road_info[road][2] #we return normal traffic weight
        elif(traffic == "heavy"):
            if(rand <= self.p1): #then choose our prediction
                return self.weight_in_heavy_traffic(self.road_info[road][2]) #road_info["Road1"][3] = normal weight, and we return heavy traffic weight
            elif(rand <= (self.p1+self.p2)): #p2 : overestimation of cost, so heavy -> normal
                return self.road_info[road][2] #we return normal traffic weight
            else: #p3: underestimation of cost so heavy -> heavy
                return self.weight_in_heavy_traffic(self.road_info[road][2]) #we return heavy traffic weight
        else:
            if(rand <= self.p1): #then choose our prediction
                return self.road_info[road][2] #return normal weight
            elif(rand <= (self.p1+self.p2)): #p2 : overestimation of cost, so normal -> low
                return self.weight_in_low_traffic(self.road_info[road][2]) #we return low traffic weight
            else: #p3: underestimation of cost so normal -> heavy
                return self.weight_in_heavy_traffic(self.road_info[road][2]) #we return heavy traffic weight

    def weight_in_heavy_traffic(self, number): 
        return float(Decimal(number)*Decimal(1.25))
    def weight_in_low_traffic(self, number): 
        return float(Decimal(number)*Decimal(0.9))

    def reset_weight_road(self):
        for key in self.weight_roads:
            self.weight_roads[key] = None

    def reset_weight(self):
        for key in self.weight:
            self.weight[key] = None
    
    def find_ucs_path(self):
        return ucs(self.graph, self.weight, self.source, self.destination)
    
    def find_ida_star_path(self):
        return ida_star(self.graph, self.weight, self.heuristic, self.source, self.destination)
    
    def predicted_path_cost(self, path):
        cost = 0
        for i in range(len(path)-1):
            cost += self.weight[path[i],path[i+1]]
        return cost
        
    def find_real_cost(self, path):
        cost = 0
        for i in range(len(path)-1):
            road = self.weight_roads[path[i], path[i+1]] #get chosen road (connecting the path nodes) from our weight_roads dictionary
            if(self.real_traffic[road] == "heavy"):
                cost += self.weight_in_heavy_traffic(self.road_info[road][2])
            elif(self.real_traffic[road] == "low"):
                cost += self.weight_in_low_traffic(self.road_info[road][2])
            else:
                cost += self.road_info[road][2]
        return cost
        
    #BIG NOUS
    def fix_propabilities(self):
        count_p1 = 0
        count_p2 = 0
        count_p3 = 0
        count_roads = 0
        for road in self.traffic_prediction:
            count_roads += 1
            if(self.traffic_prediction[road] == "low"):
                if(self.real_traffic[road] == "low"): #prediction correct
                    count_p1 += 1
                elif(self.real_traffic[road] == "heavy"): #cost was underestimated
                    count_p3 += 1 
                else: #cost was underestimated
                    count_p3 += 1 
            elif(self.traffic_prediction[road] == "heavy"):
                if(self.real_traffic[road] == "heavy"): #prediction correct
                    count_p1 += 1
                elif(self.real_traffic[road] == "low"): #cost was overestimated
                    count_p2 += 1
                else: #cost was overestimated
                    count_p2 += 1
            else:
                if(self.real_traffic[road] == "normal"): #prediction correct
                    count_p1 += 1
                elif(self.real_traffic[road] == "heavy"): #cost was underestimated
                    count_p3 += 1
                else: #cost was overestimated
                    count_p2 += 1

        new_p1 = count_p1/count_roads
        new_p2 = count_p2/count_roads
        new_p3 = count_p3/count_roads

        self.p1 = self.p1*(self.day/(self.day+1))+new_p1/(self.day+1)
        self.p2 = self.p2*(self.day/(self.day+1))+new_p2/(self.day+1)
        self.p3 = self.p3*(self.day/(self.day+1))+new_p3/(self.day+1)

    def next_day(self):
        self.reset_weight()
        self.reset_weight_road()
        self.day += 1

    def print_test(self):
        self.print_graph()
        self.print_weight()
        self.print_road_weight()
        self.print_road_info()
        self.print_heuristic_help()
        self.print_heuristic()
    
    #heuristic_help : connect two nodes with the cheapest low traffic cost that can exist in our graph (regardless of predictions)
    #will be used to create our heuristic later
    def init_heuristic(self):
        for road in self.road_info: 
            node_a, node_b = self.road_info[road][0:2]
            cost = self.road_info[road][2]
            if(self.heuristic_help[node_a,node_b] == None or self.heuristic_help[node_a,node_b] > self.weight_in_low_traffic(cost)):
                self.heuristic_help[node_a,node_b] = self.weight_in_low_traffic(cost)
                self.heuristic_help[node_b,node_a] = self.weight_in_low_traffic(cost)

        self.heuristic = dijkstra_create_heuristic(self.graph, self.heuristic_help, self.destination)
    
    def print_heuristic(self):
        print()
        print("________HEURISTIC_________")
        for node in self.heuristic:
            print(node, self.heuristic[node])
        print()

    def print_heuristic_help(self):
        print()
        print("________HEURISTIC HELP_________")
        for nodes in self.heuristic_help:
            print(nodes, self.heuristic_help[nodes])
        print()


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
    def print_road_weight(self):
        print()
        print("________ROAD WEIGHT_________")
        for node1, node2 in self.weight_roads:
            print((node1,node2) , ":", self.weight_roads[node1,node2])
        print()
    def print_road_info(self):
        print()    
        print("________ROAD INFO_________")
        for r in self.road_info:
            print(r , ":", self.road_info[r])
        print()
    def print_pred_actual(self):
        print()
        print("________PREDICTIONS_________")
        for k in self.traffic_prediction:
            print(k, ":", self.traffic_prediction[k])
        print("________ACTUAL_________")
        for k in self.real_traffic:
            print(k, ":", self.real_traffic[k])