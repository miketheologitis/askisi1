import sys
from pathlib import Path
from data import Data

class Test:
    def __init__(self, filename):
        self.data = Data(filename)
        self.offset = 4
    
    def solution(self):
        for _ in range(1):
            self.data.parse_day_predictions() #parse the daily predictions and fix weight, road_weight (dictionaries)

            time, visited_nodes, ucs_prediction, path = self.data.find_ucs_path() #solve the graph

            self.data.parse_actual_traffic()  #parse the real daily traffic
            self.data.fix_propabilities()  #fix p1,p2,p3 based on our real traffic (and predicted traffic, last day)

            real_cost = self.data.find_real_cost(path) #find the real cost of our chosen path (based on real traffic)
            """
            print("DAY", self.data.day)
            print("Uniform-Cost Search:")
            
            print(" "*self.offset,"Visited Nodes Number: ", visited_nodes)
            print(" "*self.offset,"Execution time: ", '%f' % time)
            print(" "*self.offset,"Path: ", end="")
            print(*path, sep=" -> ")
            self.print_cost_of_roads(path)
            print(" "*self.offset,"Predicted Cost:", "{:.2f}".format(round(ucs_prediction, 2)))
            print(" "*self.offset,"Real Cost: ", "{:.2f}".format(round(real_cost, 2)))
            print()
            #self.data.print_pred_actual()
            """
            self.data.print_test()
            self.data.next_day() #change the day and reset weight, weight_roads (dictionaries)

    def print_cost_of_roads(self, path):
        print(" "*self.offset,"Road Cost:", end = " ")
        for i in range(len(path)-1):
            if(i != len(path)-2):
                print(self.data.weight_roads[path[i],path[i+1]], "(", 
                "{:.2f}".format(round(float(self.data.weight[path[i],path[i+1]]), 2)),") ,", end=" ")
            else:
                print(self.data.weight_roads[path[i],path[i+1]], "(", 
                "{:.2f}".format(round(float(self.data.weight[path[i],path[i+1]]), 2)),")")


