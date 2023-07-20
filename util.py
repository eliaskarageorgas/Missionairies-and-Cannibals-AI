class Node():
    def __init__(self, state, parent, action, boat, distance, cost):
        self.state = state
        self.parent = parent
        self.action = action
        # Location of boat. Either left or right bank
        self.boat = boat
        # Distance from the initial node
        self.distance = distance
        # Total cost of the node (distance + heuristic)
        self.cost = cost


class Frontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        # Checks which node of the frontier has the minimum value of node.cost 
        # and returns the corresponding node
        if self.empty():
            raise Exception("Empty frontier")
        else:
            node = self.frontier[0]
            for n in self.frontier:
                if node.cost > n.cost:
                    node = n

            self.frontier.remove(node)
            return node

    # Used for debugging        
    def len(self):
        return len(self.frontier)