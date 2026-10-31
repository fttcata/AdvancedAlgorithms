# Vam Ende Boas Trees are a type of data structure that allows for fast operations on a set of integers. 
# They are particularly useful for operations like predecessor, successor, minimum, and maximum queries in a universe of size u.
# Each elements is of size w, w being the number of bits required to represent the maximum integer in the universe.

# This implementation is based on the recursive structure of VEB trees, where each tree is divided into a summary and clusters.
# The summary keeps track of which clusters are non-empty, while each cluster is a smaller VEB tree that contains the actual elements.

import math

class VEBTree:
    def __init__(self, u):
        self.u = u
        self.min = None
        self.max = None
        
        # Base case
        if (u <= 2):
            self.summary = None
            self.clusters = None
        else:
            # Recursive case
            # Create sqrt(u) clusters of size sqrt(u) each, and summary of size sqrt(u)
            self.summary = VEBTree(self.upper_sqrt(u))
            self.clusters = [None] * self.upper_sqrt(u)
            for i in range(self.upper_sqrt(u)):
                self.clusters[i] = VEBTree(self.lower_sqrt(u))
            
    def upper_sqrt(self, u):
        bits = (u - 1).bit_length()
        return 1 << ((bits + 1) // 2)

    def lower_sqrt(self, u):
        bits = (u - 1).bit_length()
        return 1 << (bits // 2)

    def high(self, x):  
        return x // math.ceil(math.sqrt(self.u))

    def low(self, x):
        return x % math.ceil(math.sqrt(self.u))

    def generate_index(self, x, y):
        ru = math.ceil(math.sqrt(self.u))
        return x * ru + y
    
         
    def insert(helper, x):
        ## If no key is present in the tree, set min and max to x
        if helper.min is None and helper.max is None:
            helper.min = x
            helper.max = x
            return
        ## If key is smaller than min, that means key is the new minimum
        if x < helper.min:
            temp = x
            x = helper.min
            helper.min = temp
        if (helper.u > 2):
        ## If cluster is empty, insert key into both summary and current cluster
            if helper.clusters[helper.high(x)].min is None:
                VEBTree.insert(helper.summary, helper.high(x))
                helper.clusters[helper.high(x)].min = helper.low(x)
                helper.clusters[helper.high(x)].max = helper.low(x)
            else:
                ## If cluster is not empty, insert key into the corresponding cluster
                VEBTree.insert(helper.clusters[helper.high(x)], helper.low(x))
        if (x > helper.max):
            helper.max = x
        
    def isMember(helper, x):
        # If key is greater than the universe size, we cannot search the key
        if x < 0 or x >= helper.u:
            return False
        # If key is equal to min or max, key exists in the cluster
        if helper.min == x or helper.max == x:
            return True
        # If the universe size is 2, we cannot search further
        if helper.u <= 2:
            return False
        # Recursively search over the cluster in which the key can exist
        return VEBTree.isMember(helper.clusters[helper.high(x)], helper.low(x))
    
    def delete(helper, x):
        if helper.min is None:
            return
        
        if helper.min == helper.max == x:
            helper.min = None
            helper.max = None
            return
        
        if helper.u == 2:
            if x == 0:
                helper.min = 1
            else:
                helper.min = 0
            helper.max = helper.min
            return
        
        # If x the minimum, delete x and find the next minimum from the summary and clusters
        if x == helper.min:
            if helper.summary.min is None:
                helper.min = helper.max
                return
            else:
                first_cluster = helper.summary.min
                x = helper.generate_index(first_cluster, helper.clusters[first_cluster].min)
                helper.min = x
                helper.delete(helper.clusters[first_cluster], helper.low(x))
            
        # If x is not the minimum, delete x from the corresponding cluster
        cluster_index = helper.high(x)
        offset = helper.low(x)
        helper.clusters[cluster_index].delete(offset)
        
        if helper.clusters[cluster_index].min is None:
            helper.summary.delete(cluster_index)
            if x == helper.max:
                summary_max = helper.summary.max
                if summary_max is None:
                    helper.max = helper.min
                else:
                    helper.max = helper.generate_index(summary_max, helper.clusters[summary_max].max)
        return

    def predecessor(helper, x):
        if helper.min is None:
            return print(x, "Tree is empty")
        
        if helper.u == 2:
            if x == 1 and helper.min == 0:
                return 0
            else: return print(x, "No predecessor exists")
        
        ## if x is greater than the global maximum, return global maximum
        if x > helper.max:
            return helper.max
        
        ## If x is less than the global minimum, then there is no predecessor
        if x < helper.min:
            return print(x, "No predecessor exists")
        
        ## Recursively search for the predecessor in x's cluster
        high = helper.high(x)
        low = helper.low(x)
        cluster = helper.clusters[high]

        if cluster.min is not None and low > cluster.min:
            offset = VEBTree.predecessor(cluster, low)
            return helper.generate_index(high, offset)
        
        ## If there is no predecessor in the cluster, return next non-empty cluster's maximum element
        if cluster.min is not None and low == cluster.min:
            if helper.summary.min is None:
                return print(x, "No predecessor exists")
            else:
                pred_cluster = helper.summary.predecessor(high)
                if pred_cluster is None:
                    return helper.min
                else:
                    offset = helper.clusters[pred_cluster].max
                    return helper.generate_index(pred_cluster, offset)
        
        return print(x, "No predecessor exists")
            
    def successor(helper, x):
        if helper.min is None:
            return print(x, "Tree is empty")
        
        if helper.u == 2:
            if x == 0 and helper.max == 1:
                return 1
            else: return print(x, "No successor exists")
        
        ## x < global min, return global min
        if x < helper.min:
            return helper.min
        
        ## x > global max, no successor exists
        if x > helper.max:
            return print(x, "No successor exists")
        
        ## Recursively search for the successor in x's cluster
        high = helper.high(x)
        low = helper.low(x)
        cluster = helper.clusters[high]
        
        if cluster.max is not None and low < cluster.max:
            offset = VEBTree.successor(cluster, low)
            return helper.generate_index(high, offset)
        
        ## If there is no successor, return next non-empty cluster's minimum element
        succ_cluster = helper.summary.successor(high)
        if succ_cluster is None:
            return print(x, "No successor exists")
        else:
            offset = helper.clusters[succ_cluster].min
            return helper.generate_index(succ_cluster, offset)

if __name__ == "__main__":
    tree = VEBTree(16)
    
    result = tree.predecessor(5) # Should return "No predecessor exists"
    
    tree.insert(2)
    tree.insert(3)
    tree.insert(10)
    
    tree.delete(10) # Should delete 10
    
    result = tree.predecessor(3) # Should return 2
    print("3 Should return 2: ", result)  # Output: 2
    
    result = tree.successor(2) # Should return 3
    print("2 Should return 3: ", result)  # Output: 3
    
    result = tree.predecessor(5) # Should return 3
    print("5 Should return 3: ", result)  # Output: 3
    
    result = tree.predecessor(1) # Should return "No predecessor exists"
    
    result = tree.successor(4) # Should return "No successor exists"
    
    
    print(tree.isMember(2))  # Output: True
    print(tree.isMember(3))  # Output: True
    print(tree.isMember(7)) # Output: False
    
    



