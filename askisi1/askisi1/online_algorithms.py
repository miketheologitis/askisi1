from pathlib import Path
from data import Data
import math
import time


class OnlineLRTAstar():

    def __init__(self, d):
        self.d = d

    def solve(self):
        start_time = time.perf_counter() #time

        parent = None
        current = self.d.source
        H = {}
        cost = {}
        all_moves_cost = 0
        path = []

        while True:
            #print("Parent: ", parent, "Current: ", current)
            path.append(current)
            if current == self.d.destination:
                return (time.perf_counter()-start_time), all_moves_cost, path
            if current not in H:
                H[current] = self.d.heuristic[current]
            if parent is not None:
                H[parent] = cost[parent, current] + self.d.heuristic[current]
            parent = current
            current = self.chooseNextNode(current, H)
            cost[parent, current] = self.findRealMinCost(parent, current) #we are allowed to find it because we have traversed the road, and now we are at the next node
            all_moves_cost += cost[parent, current]
            
    def chooseNextNode(self, current, H):
        min_estimated_cost = math.inf
        min_node = None
        for node in self.d.graph[current]:
            if node in H:
                if(min_estimated_cost > H[node]):
                    min_estimated_cost = H[node]
                    min_node = node
            else:
                if(min_estimated_cost > self.d.heuristic[node]):
                    min_estimated_cost = self.d.heuristic[node]
                    min_node = node
        return min_node

    def findRealMinCost(self, parent, current): #considering someone at node a can see the traffic to all the connecting roads towards b
        min_cost = math.inf
        for road in self.d.road_info:
            if(self.d.road_info[road][0:2] == (parent,current) or self.d.road_info[road][0:2] == (current,parent)):
                normal_weight = self.d.road_info[road][2]
                if(self.realTrafficCost(road, normal_weight) < min_cost):
                    min_cost = self.realTrafficCost(road, normal_weight)
        return min_cost

    def realTrafficCost(self, road, weight):
        if(self.d.real_traffic[road] == "low"):
            return self.d.weight_in_low_traffic(weight)
        elif(self.d.real_traffic[road] == "heavy"):
            return self.d.weight_in_heavy_traffic(weight)
        else:
            return weight
    #as orisoume to action a = roadChosen. exontas to roadinfo exoume tis plirofories poy mas endiaferoun. prosoxi oti duo nodes ta sundeoun polloi dromoi
    # this is a problem for the future we will see