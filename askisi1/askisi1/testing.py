import sys
from pathlib import Path
from data import Data

class Test:
    def __init__(self, filename):
        self.data = Data(filename)
    
    def print_test(self):
        for _ in range(80):
            self.data.parse_day_predictions()
            time, visited_nodes, ucs_prediction, path = self.data.find_ucs_path()
            self.data.parse_actual_traffic()
            #self.data.print_test()
            real_cost = self.data.find_real_cost(path)
            print("Visited Nodes Number: ", visited_nodes)
            print("Execution time: ", '%f' % time)
            print("Path: ", end="")
            print(*path, sep=" -> ")
            print("Predicted Cost:", "{:.2f}".format(round(ucs_prediction, 2)))
            print("Real Cost: ", "{:.2f}".format(round(real_cost, 2)))
            print()
            #self.data.print_pred_actual()
            self.data.next_day()
