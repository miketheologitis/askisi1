from pathlib import Path
from collections import defaultdict
from decimal import Decimal
from algorithms import ucs, dijkstra_create_heuristic, ida_star
import random


#https://cyluun.github.io/blog/uninformed-search-algorithms-in-python
#https://www.youtube.com/watch?v=dRMvK76xQJI ucs algorithm

"""
    A class used to modify, parse and store data from our files

    ...

    Attributes
    ----------
    file : file
        the file which is used to parse the source, destination, road info AND then all the daily predictions
    file_traff : file
        the file which is used to parse the REAL traffic , the next day
    source : String
        our starting node
    graph : Dictionary
        Our dictionary of sets representing a graph with key = NodeA, value = set(NodeB,NodeG, ..) . Example: graph[NodeA] = (NodeB, NodeG, ..)
    weight: Dictionary
        My dictionary with key = set(NodeA, NodeB), value = (int) weight to go from NodeA to NodeB 
        IMPORTAND: 
        Since we have many ways of connecting NodeA, NodeB in our graph (possibly many different roads), each day, based on the predictions
        I choose the cheapest path to connect NodeA, NodeB and this value is stored in this weight dictionary. Every day this weight might
        change because for example: the road with which we connected NodeA, NodeB the previous day, now has a prediction of "heavy" traffic and there is a cheaper road
        connecting these two nodes. EACH DAY the weight dictionary resets, and gets recreated based on our next days' predictions!
    weight_roads: Dictionary
        My dictionary with key = set(NodeA, NodeB), value = RoadA . The string value RoadA is the cheapest road we CHOSE the last day to connect these two nodes, 
        which also corresponds to weight[NodeA, NodeB]. Each day the cheapest road gets chosen (based on predictions) to connect two nodes and the road name gets stored
        in weight_roads[(. , .)], and the cost of traversing it gets stored in weight[(. , .)]. EACH DAY the weight_roads dictionary resets, and gets recreated based on our next days' predictions!
    road_info: Dictionary
        All the road info we read in the first file lines. key = RoadA, value = (NodeA, NodeB, normal_cost) . RoadA is the String name of each rode, and (NodeA, NodeB, normal_cost)
        is a set with the nodes that this RoadA connects, and the NORMAL cost of traversing it.
    traffic_prediction: Dictionary
        Each days' traffic predictions. key = RoadName, value = predictions (ex. "low")
    real_traffic: Dictionary
        Each days' real traffic. key = RoadName, value = traffic (ex. "low")
    day: int
        What day it is
    heuristic_help: Dictionary
        This dictionary is used to create our heuristic dictionary and gets created once with key = set(NodeA, NodeB) , value = cheapest weight connecting them
        IMPORTAND:
        Cheapest weight connecting them means, that we take for every road the "low" cost , and FROM ALL those roads connecting NodeA, NodeB we store the CHEAPEST cost 
        of connecting those two nodes. This is regardless of any prediction since we take "low" cost to ALL roads. This dictionary will be used to create our heuristic dictionary
    heuristic: Dictionary
        This is the heuristic dictionary with key = NodeA, value = cheapest cost to go from goal to nodeA . 
        It is created with my dijkstra algorithm, finding the cheapest cost to go from goal to each node and storing this cost in heuristic dictionary. It uses the heuristic_help
        dictionary aswell. See dijkstra_create_heuristic(graph, heuristic_help, goal) , in algorithms.py for more information.
    p1: float
        This is the probability of making a CORRECT prediction
    p2: float
        This is the probability of overestimating the cost (or else overestimating the traffic) in a prediction
    p1: float
        This is the probability of underestimating the cost (or else underestimating the traffic) in a prediction
    Methods
    -------
"""

class Data:
    def __init__(self, filename):
        #https://stackoverflow.com/questions/40416072/reading-file-using-relative-path-in-python-project
        self.file = open(Path(__file__).parent  / ("../data/"+filename), "r")
        self.file_traff = open(Path(__file__).parent  / ("../data/"+filename), "r") #file_predictions, file_pred is used to read the real traffic

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
        
        self.parse_source()  #parse the source vertex
        self.parse_destination() #parse the destination vertex
        self.parse_roads() #parse all info about roads
        self.file.readline() #skip a line
        
        self.init_heuristic() #create our heuristic function (created by dijkstra) to be used by IDA* algorithm

        self.go_to_actual_traffic() #move file_traff (open file) to be ready to parse real daily traffic
        
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
            if(self.real_traffic[road] == "heavy"):  #check according to the traffic each day what was the actual cost of using those roads
                cost += self.weight_in_heavy_traffic(self.road_info[road][2])
            elif(self.real_traffic[road] == "low"): #check according to the traffic each day what was the actual cost of using those roads
                cost += self.weight_in_low_traffic(self.road_info[road][2])
            else: #check according to the traffic each day what was the actual cost of using those roads
                cost += self.road_info[road][2]
        return cost
        
    #BIG NOUS
    #This function reads traffic_prediction and real_traffic and compares the two dictionaries each day, counting how many instances of different predictions we have for
    #p1,p2,p3 called count_p1, count_p2, count_p3. According to them we find the new propabilities new_p1,new_p2,new_p3.
    # Then the new_p1, new_p2, new_p3 are used to find the AVERAGE of them with the current p1,p2,p3 ACCORDING to what day it is
    # Example: Lets say we have at the end of day 3, p1 = 0.63 and we find new_p1 = 0.7. 
    # Then the p1 = p1*(3/4) + new_p1/4  OR  p1 = p1*(day/(day+1)) + new_p1/(day+1)   , to put numbers in we have at day 4 ->  p1 = 0.63*(3/4)+0.73/4 -> p1 = 0.655
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
    
    """
    Down here are all the print tests ive used to make sure my code is running well and as intended. No use reading it.
    """
    def print_test(self):
        self.print_graph()
        self.print_weight()
        self.print_road_weight()
        self.print_road_info()
        self.print_heuristic_help()
        self.print_heuristic()
        self.print_pred_actual()

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