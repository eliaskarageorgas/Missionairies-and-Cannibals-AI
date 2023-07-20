import sys
import copy
import time
from util import Node, Frontier


def main():
    # Getting the information necessary from the command line
    if len(sys.argv) != 4:
        sys.exit("Usage: python Missionaries_and_Cannibals.py {integer N} {integer M} {integer K}")

    try:
        N = int(sys.argv[1])
    except ValueError:
        print("Not an integer")

    try:
        M = int(sys.argv[2])
    except ValueError:
        print("Not an integer")
    
    try:
        K = int(sys.argv[3])
    except ValueError:
        print("Not an integer")
    
    start_time = time.time()
    solution_node = A_star(N, M, K)
    
    if solution_node != None:
        current_node = solution_node
        path = []
        while current_node != None:
            path.append(current_node)
            current_node = current_node.parent
        
        for i in range(len(path) - 1, -1, -1):
            if path[i].action != None:
                print("Action: ", "M" * path[i].action[0], " (", path[i].action[0], ")  ", "C" * path[i].action[1], " (", path[i].action[1], ")  to the ", path[i].boat, sep='')
            print("Left bank: ", "M" * path[i].state[0][0], " (", path[i].state[0][0], ")  ", "C" * path[i].state[0][1], " (", path[i].state[0][1], ")", sep='')
            print("Right bank: ", "M" * path[i].state[1][0], " (", path[i].state[1][0], ")  ", "C" * path[i].state[1][1], " (", path[i].state[1][1], ")", sep='')
            print("The boat is on the", path[i].boat, "bank" )
            print()
        
        print("Total trips:", path[0].distance)
        end_time = time.time()
        print("Total time:", round(end_time - start_time, 3), "seconds")
    else:
        print("\nNo solution is found with the given arguments.")
        end_time = time.time()
        print("Total time:", round(end_time - start_time, 3), "seconds")
            

def actions(state, boat, M):
    '''
    Returns a list with all the possible actions [m, c] from the current state
    m = missionaries to go across, c = cannibals to go across
    '''
    available_actions = []

    for m in range(M+1):
        for c in range(M - m, -1, -1):
            # The missionaries shouldn't be less than the cannibals in the boat
            if c <= m or m == 0:
                if boat == "left":
                    # Check if we can move m missionaries and c cannibals across (at least one should be moved)
                    # If it is possible add a new action to the list
                    if state[0][0] - m >= 0 and state[0][1] - c >= 0 and [m, c] != [0,0]:
                        available_actions.append([m, c])
                else:
                    if state[1][0] - m >= 0 and state[1][1] - c >= 0 and [m, c] != [0,0]:
                        available_actions.append([m, c])
    
    return available_actions


def result(state, boat, action):
    # Return the new state which is the result of applying the given action to the given state
    m = action[0]
    c = action[1]

    new_state = copy.deepcopy(state)

    if boat == "left":
        new_state[0][0] -= m
        new_state[1][0] += m
        new_state[0][1] -= c
        new_state[1][1] += c
    else:
        new_state[0][0] += m
        new_state[1][0] -= m
        new_state[0][1] += c
        new_state[1][1] -= c

    # If the missionaries on the left or right bank are less than the cannibals 
    # and the missionaries are not 0
    # return None
    if (new_state[0][0] < new_state[0][1] and new_state[0][0] != 0) or (new_state[1][0] < new_state[1][1] and new_state[1][0] != 0):
        return None

    return new_state


def terminal(state, N):
    # Return True if the given state is terminal or False if it isn't
    if state[1] == [N, N]:
        return True
    
    return False


def explored(state, boat, explored):
    # Return True if the given state has already been explored and False if it hasn't
    for n in explored:
        if n.state == state and n.boat == boat:
            return True
    
    return False


def heuristic(state, boat, M):
    '''
    Return a heuristic value based on the location of the boat and
    the people that should be moved

    Ignore the restriction of having equal or more missionaries 
    than cannibals on each side of the bank

    Also ignore the trips from the right bank to the left 
    (exception if the boat is on the right bank at the start)

    So the heuristic value is calculated by adding the number of people on the left bank (num_left),
    then dividing by M to calculate the minimum number of trips from the left bank to the right (trips)
    '''
    # Number of people on the left bank
    num_left = state[0][0] + state[0][1]

    trips = 0
    
    # If the boat is on the right bank at the start, it should be moved to the left
    # before counting the trips from the left to the right bank that should be made
    # to move all of the characters across. By adding 1 to the 'num_left' and the 'trips'
    # variables we indicate that first trip
    if boat == "right" and num_left != 0:
        num_left += 1
        trips += 1

    # If after x trips there are y people (y < M) on the left bank
    # one more trip should be made
    if num_left % M != 0:
        trips += 1

    trips += num_left // M
    return trips


def evaluate(state, boat, distance, M):
    # Return the total cost of the given state by adding the value
    # from the heuristic function to the distance value
    heuristic_value = heuristic(state, boat, M)

    return heuristic_value + distance


def A_star(N, M, K):
    '''
    Returns best path of actions based on the given restrictions
    Returns None if there is no such path
    '''

    '''
    Each row corresponds to the combination in each bank of the river
    First row for left side and second row for right side
    First column for missionaries and second column for cannibals
    state = [[a,b], [c, d]]
    a = missionaries on left bank (state[0][0])
    b = cannibals on left bank (state[0][1])
    c = missionaries on right bank (state[1][0])
    d = cannibals on right bank (state[1][1])
    '''
    initial_state = [[N,N], [0,0]]
    node = Node(state = initial_state, parent = None, action = None, boat = "left", distance = 0, cost = evaluate(initial_state, "left", 0, M))
    frontier = Frontier()
    frontier.add(node)
    
    # Initialize explored set
    explored_nodes = set()

    # Initialize solutions set
    solution_nodes = set()

    while True:
        # If the frontier is empty there is no solution
        if frontier.empty():
            break

        # Choose a node from the frontier based on the cost attribute
        node = frontier.remove()

        # If the current node is terminal add it to the solutions set
        if (terminal(node.state, N)):
            solution_nodes.add(node)
        else:
            explored_nodes.add(node)

            available_actions = actions(node.state, node.boat, M)
            # Used for debugging
            #print("State: ", node.state, node.boat, node.distance, node.cost)
            
            for action in available_actions:
                new_state = result(node.state, node.boat, action)
                if new_state != None:
                    if node.boat == "left":
                        boat = "right"
                    else:
                        boat = "left"

                    new_distance = node.distance + 1
                        
                    # If the new state (and boat location) has already been explored
                    # or the distance is greater than K
                    # we won't add it to the frontier
                    if not explored(new_state, boat, explored_nodes) and new_distance <= K:
                        new_cost = evaluate(new_state, boat, new_distance, M)  
                        # Used for debugging           
                        #print(new_state, boat, new_distance, new_cost)
                        new_node = Node(new_state, node, action, boat, new_distance, new_cost)
                        frontier.add(new_node)

    if len(solution_nodes) == 0:
        return None
    else:
        best_solution = solution_nodes.pop()
        for s in solution_nodes:
            if best_solution.cost > s.cost:
                best_solution = s

        return best_solution
    
    

main()