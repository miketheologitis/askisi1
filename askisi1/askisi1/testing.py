import sys
from pathlib import Path
from data import Data
from online_algorithms import OnlineLRTAstar

class Test:
    def __init__(self, filename):
        self.data = Data(filename)
        self.offset = 4
        self.lrta = OnlineLRTAstar(self.data)
        
    def do_everything(self):
        ucs_sum_cost = 0
        ida_star_sum_cost = 0

        for _ in range(80):
            self.data.parse_day_predictions() #parse the daily predictions and fix weight, road_weight (dictionaries)

            ucs_time, ucs_visited_nodes, ucs_cost, ucs_path = self.data.find_ucs_path() #solve the graph using ucs

            ida_star_time, ida_star_visited_nodes, ida_star_cost, ida_star_path = self.data.find_ida_star_path() #solve the graph using ida*

            ucs_sum_cost += ucs_cost
            ida_star_sum_cost += ida_star_cost

            self.data.parse_actual_traffic()  #parse the real daily traffic
            self.data.fix_propabilities()  #fix p1,p2,p3 based on our real traffic (and predicted traffic, last day)

            lrta_time, lrta_sum_cost , lrta_path = self.lrta.solve()

            ucs_real_cost = self.data.find_real_cost(ucs_path) #find the real cost of our chosen path (based on real traffic)
            ida_star_real_cost = self.data.find_real_cost(ida_star_path)
            
            #self.data.print_test()
            print("DAY", self.data.day)
            self.print_test("UCS", ucs_visited_nodes, ucs_time, ucs_path, ucs_cost, ucs_real_cost)
            self.print_test("IDA*", ida_star_visited_nodes, ida_star_time, ida_star_path, ida_star_cost, ida_star_real_cost)
            print("LRTA* :")
            print(" "*self.offset,"Execution time: ", '%f' % lrta_time)
            print(" "*self.offset,"Path: ", end="")
            print(*lrta_path, sep=" -> ")
            print(" "*self.offset, "Cost Of All Moves:", lrta_sum_cost)
            print()

            self.data.next_day() #change the day (data.day++) and reset weight, chosen_road (dictionaries)
        print("Average daily Uniform Cost Search (UCS) cost: ", "{:.2f}".format(round(ucs_sum_cost/80.0, 2)))
        print("Average daily Iterative Deepening A* (IDA*) cost: ", "{:.2f}".format(round(ida_star_sum_cost/80.0, 2)))
        print()

    def print_test(self, alg_name, visited_nodes, time, path, prediction_cost, real_cost):
        print(alg_name,":")
        print(" "*self.offset,"Visited Nodes Number: ", visited_nodes)
        print(" "*self.offset,"Execution time: ", '%f' % time)
        print(" "*self.offset,"Path: ", end="")
        print(*path, sep=" -> ")
        self.print_cost_of_roads(path)
        print(" "*self.offset,"Predicted Cost:", "{:.2f}".format(round(prediction_cost, 2)))
        print(" "*self.offset,"Real Cost: ", "{:.2f}".format(round(real_cost, 2)))

    def print_cost_of_roads(self, path):
        print(" "*self.offset,"Road Cost:", end = " ")
        for i in range(len(path)-1):
            if(i != len(path)-2):
                print(self.data.chosen_road[path[i],path[i+1]], "(", 
                "{:.2f}".format(round(float(self.data.weight[path[i],path[i+1]]), 2)),") ->", end=" ")
            else:
                print(self.data.chosen_road[path[i],path[i+1]], "(", 
                "{:.2f}".format(round(float(self.data.weight[path[i],path[i+1]]), 2)),")")



