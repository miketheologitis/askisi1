from queue import PriorityQueue
import time
import math

#https://towardsdatascience.com/introduction-to-priority-queues-in-python-83664d3178c3  -> PriorityQueue
"""
This is a Uniform Cost Search , with some differences (I will note them bellow)
I expand nodes according to their path costs form the root node. 
I use fringe as PriorityQueue (see python doc), visited as set (O(1) existance search), parent dictionary to backtrace the path
and dict_node_weight which helps us decide which parent (or else, path) to keep if we find a node which HAS to be inserted in the fringe,
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
                    #else: do nothing because we want to
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
#https://www.codingame.com/playgrounds/1608/shortest-paths-with-dijkstras-algorithm/dijkstras-algorithm
def dijkstra_create_heuristic(graph, heuristic_help, goal): #create approximaiton of distance of every node to goal, from low predictions (cheapest)
    costs = {}
    unvisited = {}
    visited = set() #relaxed nodes

    #initialize costs
    #initialize unvisited
    for node in graph:
        unvisited[node] = math.inf
        costs[node] = math.inf
    costs[goal] = 0
    unvisited[goal] = 0

    while len(unvisited)>0: #while there are nodes in unvisited
        current_node = min(unvisited, key=unvisited.get) #get the node with the least cost , which in the first case will obviously be goal (with cost 0)
        visited.add(current_node) #add current_node to visited
        costs[current_node] = unvisited[current_node] #since current_node was chosen, its cost on unvisited dictionary is final, and the cheapest one. so store it on costs[current_node]
        del unvisited[current_node] #delete current_node key from unvisited dictionary

        for node in graph[current_node]:
            if(node in visited): 
                continue
            if(costs[current_node]+heuristic_help[current_node, node] < unvisited[node]): #if: the cheapest cost to current_node + cost from current_node to node < the stored cost in node, then change it!
                unvisited[node] = costs[current_node]+heuristic_help[current_node, node]
    return costs #return our final heuristic costs, which is the heuristic function of each node




"""
Performs the iterative deepening A Star (A*) algorithm to find the shortest path from a start to a target node.
graph: Our graph
heuristic: The cheapest cost to go from a node to goal, already calculated in Data.init_heuristic()
"""

#Also, a way to think about ida_star_path is that it stores the path each node is right now. If it goes very deep the path will become huge, 
#untill we start popping (this will happen when we reach a f(n) limit)
ida_star_path = [] #global variable of ida star path (cuz of recursion)
ida_star_visited_nodes = 0

#IMPORTAND: #https://en.wikipedia.org/wiki/Iterative_deepening_A* - PSEUDOCODE!!!!!!!

def ida_star(graph, weight, heuristic, start, goal):
    start_time = time.perf_counter() #time
    global ida_star_visited_nodes
    global ida_star_path
    ida_star_path.clear() #clear the path from the previous day
    ida_star_visited_nodes = 0

    threshold = heuristic[start]
    ida_star_path.append(start)

    while True:
        distance, boolean = ida_star_rec(graph, weight, heuristic, goal, 0, threshold)
        if (boolean):
            # we found the goal
            return (time.perf_counter()-start_time), ida_star_visited_nodes, distance, ida_star_path
        else:
            # if it hasn't found the node, it returns the next-bigger threshold
            threshold = distance

"""
Performs DFS up to a depth where a threshold is reached using f(n) = g(n)+h(n) (as opposed to interative-deepening DFS which stops at a fixed depth).
graph: Our graph
heuristic: The cheapest cost to go from a node to goal
node: The node to continue from.
goal: The node we are searching for.
distance:  Distance from start node to current node.
threshold: Threshold to reach before stopping and starting again
"""
def ida_star_rec(graph, weight, heuristic, goal, distance, threshold):
    global ida_star_visited_nodes
    global ida_star_path

    node = ida_star_path[-1] #choose the last node that was put in the path
    f = distance + heuristic[node]

    if f > threshold: #Breached threshold with heuristic
        return f, False

    if node == goal: # We have found the goal node
        return distance, True

    # ...then, for all child nodes....
    min = math.inf
    for child in graph[node]:
        if child not in ida_star_path:
            ida_star_visited_nodes += 1
            ida_star_path.append(child) #put child as the last one in the path
            t, boolean = ida_star_rec(graph, weight, heuristic, goal, distance + weight[node,child], threshold)
            if (boolean): #We have found the goal node, from one of the children (or children of children of ...)
                return t, True
            if (t < min):
                min = t
            ida_star_path.pop() #start popping our useless path (many pops will happen in a row if we have entered a huge path)
    return min, False