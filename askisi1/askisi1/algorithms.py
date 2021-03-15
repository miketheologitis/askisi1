from queue import PriorityQueue
import time
import math

#https://towardsdatascience.com/introduction-to-priority-queues-in-python-83664d3178c3  -> PriorityQueue
"""
This is a Uniform Cost Search , with some differences (I will note them bellow)
I expand nodes according to their path costs form the root node. 
I use fringe as PriorityQueue (see python doc), visited as set (O(1) existance search), parent dictionary to backtrace the path
and dict_node_weight which helps us decide on which parent (or else, path) to keep if we find a node which HAS to be inserted in the fringe,
but it is ALREADY in the fringe from a different path. 

Some key points about backtracing the path when we find the goal:
1.  My idea is that I create a dictionary which has as key : every node that goes to the fringe and the value is: the parent which "put" the node to the fringe.
2.  When goal is found (or else expanded) we return the backtrace(parent,start,end) which easily finds the path that got us to that goal. And I also return the path cost
    or simply, the goal's ucs_weight.

This creates a problem though, what if a nodeX is in the fringe waiting, and when we expand another nodes' children we find the nodeX? The problem is that we update the 
parent dictionary and the NEW parent is our expanded node (from which we found the duplicate), and the OLD parent is LOST. More simply, we found a different path to the nodeX 
which right now is in the fringe waiting. Or even more simply the last node that finds a new path to nodeX (considering nodeX is still in the fringe waiting) 
will update the parent equal to the current_node which expanded NodeX. The solution:

My idea is to create a dictionary called dict_node_weight which for every node that goes in the fringe we also assign its ucs_weight (weight from start). We keep this weight
in memory and when we find a duplicate path (see above) we check whether the ucs_weight from the NEW path we just found, is bigger or smaller than the weight inside the
dictionary , for the nodeX that is in the fringe. If the new path that we found to nodeX, has to assign nodeX a SMALLER ucs_weight, then we do exactly that, we UPDATE the 
parent (equal to the current_node which expanded our new path to nodeX) , we also update the new (cheaper) weight to the dict_node_weight, and we ADD nodeX to the
fringe AGAIN! This way we "forget" the more costly path which is right now in the fringe (parent was changed in dictionary). Otherwise, we DONT change the parent 
(because the nodeX that is in the fringe came from a CHEAPER path) and we DONT put the nodeX to the fringe (it is already there from a cheaper path), so basically we do nothing.

IMPORTAND NOTE: the fringe (PriorityQueue) can have the nodeX twice in it BUT with the same parent. We are certain that our lesser ucs_weight will get 
popped and expanded first. AND also, for time sake, every time we get a node from the fringe, we also check if it has been VISITED before. This can obviously
happen, as I explained above, and in such case we ignore this node COMPLETELY.
"""
def ucs(graph, weight, start, end):
    start_time = time.perf_counter() #time
    fringe = PriorityQueue() #priority queue , with priority of the cheaper ucs_weight
    visited = set()
    parent = {} #dictionary of node's parent , to backtrace the path
    dict_node_weight = {}  #dictionary of node's path cost from the starting node (Explained thoroughly above)

    visited_nodes = 0

    fringe.put((0, start)) #put the source in the fringe with ucs_weight=0
    while True:
        ucs_w, current_node = fringe.get()
        
        if(current_node in visited): #this is because THERE IS A CHANCE we can have the same node in fringe, and that means that the current_node could have been already processed
            continue

        visited.add(current_node) #add to visited the current node 
        visited_nodes += 1

        if(current_node == end): #then we reached goal 
            return (time.perf_counter()-start_time), visited_nodes, ucs_w, backtrace(parent, start, end)

        for node in graph[current_node]: #for every child of current_node
            if node not in visited: #because of cyrcles
                new_ucs_weight = ucs_w+weight[(current_node, node)]  #current_node's ucs_weight + the weight from current_node to its child node
                if (node in dict_node_weight): #this means that the node is already in the fringe, and now we have a different path to it , with parent = current_node
                    if(dict_node_weight[node]> new_ucs_weight): #this means that the best path (cheaper) to our node is with parent=current_node (and not the previous parent)
                        dict_node_weight[node] = new_ucs_weight #store the new cheaper weight to our node
                        parent[node] = current_node #update parent
                        fringe.put((new_ucs_weight, node))
                else:
                    dict_node_weight[node] = new_ucs_weight #store the weight
                    parent[node] = current_node #update parent
                    fringe.put((new_ucs_weight, node))

#this is a simple function, COPY PASTE from https://stackoverflow.com/questions/8922060/how-to-trace-the-path-in-a-breadth-first-search
def backtrace(parent, start, end):
    path = [end]
    while path[-1] != start:
        path.append(parent[path[-1]])
    path.reverse()
    return path


#https://stackoverflow.com/questions/3282823/get-the-key-corresponding-to-the-minimum-value-within-a-dictionary
#https://likegeeks.com/python-dijkstras-algorithm/
#https://www.codingame.com/playgrounds/1608/shortest-paths-with-dijkstras-algorithm/dijkstras-algorithm
def dijktra_create_heuristic(graph, heuristic_help, goal): #create approximaiton of distance of every node to goal, from low predictions (cheapest)
    costs = {}
    unvisited = {}
    visited = set() #relaxed nodes

    #initialize costs
    for node in graph:
        unvisited[node] = math.inf
        costs[node] = math.inf
    costs[goal] = 0
    unvisited[goal] = 0

    while len(unvisited)>0:
        current_node = min(unvisited, key=unvisited.get)
        visited.add(current_node)
        costs[current_node] = unvisited[current_node] #update the final cost of the current_node, since it is for sure the cheapest 
        del unvisited[current_node] #delete current_node key from unvisited dictionary

        for node in graph[current_node]:
            if(node in visited):
                continue
            if(costs[current_node]+heuristic_help[current_node, node] < unvisited[node]):
                unvisited[node] = costs[current_node]+heuristic_help[current_node, node]
    return costs


#https://www.algorithms-and-technologies.com/iterative_deepening_a_star/python