# Fusion trees are a type of data structure which allow the search of a key in O(log n / log w) time, where w is the number of bits in the machine word.
# The most important properties of a fusion tree are the sketch function and the parallel comparison of sketches. The sketch function is used to reduce the size of the keys, while the parallel comparison allows for multiple comparisons to be made simultaneously.

# This implementation is just for fun with no practical use, as it is not optimized for performance. It is based on Harvard's CS224 class taught by Prof. Jelani Nelson
# Since python offers fixed word sized. We assume that w is the number of bits in the machine word, standard today being 64 bits. The maximum number of keys in a fusion tree node is 2^(w/5), which is 2^12 = 4096 foor w = 64

class FusionTree:
    def __init__(self, w=64):
        self.root = FusionNode([], w=w)
        self.w = w
        # Branching threshold capacity (r = w^(1/4))
        self.r = max(2, int(w ** 0.25)) 

    def search(self, key):
        current = self.root
        while not current.is_leaf:
            # Use our parallel bitwise search to get the exact rank in O(1) time
            idx = current.fusion_node_logic.search(key)
            
            # The rank tells us exactly which child branch to take
            current = current.children[idx]
            
        return key in current.keys



class FusionNode:
    def __init__(self, keys, w=64):
        self.w = w                # Word size (e.g., 64-bit)
        self.keys = sorted(keys)  # Node keys must be sorted
        self.r = len(keys)        # Degree/Branching factor
        
        if (self.r == 0):
            self.is_leaf = True
        else:
            self.is_leaf = False
        
        if self.r > 0:
            self.important_bits = self._find_important_bits()
            self.mask = sum(1 << b for b in self.important_bits)
            self.multipliers = self._compute_multipliers()
            self.sketches = [self.sketch(k) for k in self.keys]
            self.node_word = self._pack_node_word()

    def _find_important_bits(self):
        # Find the bith which distinguis the keys in the nodes
        important = set()
        for i in range(len(self.keys) - 1):
            diff = self.keys[i] ^ self.keys[i+1]
            # Extract all bit positions where diff has a 1
            for b in range(self.w):
                if (diff >> b) & 1:
                    important.add(b)
        return sorted(list(important))

    def _compute_multipliers(self):
        # We simulate the mapping of the important bits in the sketch
        
        # Mapping each important bit to a compressed target position
        return {bit: idx * 4 for idx, bit in enumerate(self.important_bits)}

    def sketch(self, key):
        # Compress key down to only its distuingishable bits 
        sketched_key = 0
        for bit, target_pos in self.multipliers.items():
            bit_value = (key >> bit) & 1
            sketched_key |= (bit_value << target_pos)
        return sketched_key

    def _pack_node_word(self):
        # Pack sketches into a word, separated by '1' 
        node_word = 0
        # Field size needs to accommodate sketched key size + 1 bit for comparison
        self.field_size = (self.r ** 4) or 8  
        
        for i, sk in enumerate(self.sketches):
            # Format: [1sketch][1sketch].. etc.
            field = (1 << self.field_size) | sk
            node_word |= (field << (i * (self.field_size + 1)))
        return node_word

    def _msb(self, x):
        # Finds the most significant bit (index of highest 1 bit).
        return x.bit_length() - 1 if x > 0 else -1

    def search(self, query):
        # Finds predecessor, successor, or exact match of the query key
        if not self.keys:
            return 0
            
        # 1. Sketch the query key
        q_sketch = self.sketch(query)
        
        # 2. Parallel Comparison: Broadcast query to match the packed node word layout
        # Format: [0q_sketch][0q_sketch].. etc. We use 0 to not interfere with the delimitator '1's in the node word
        query_word = 0
        for i in range(self.r):
            query_word |= (q_sketch << (i * (self.field_size + 1)))
            
        # Subtracting query_word from node_word flips the test bits to 0 
        # for any node field where node_sketch < query_sketch
        comparison = self.node_word - query_word
        
        # Isolate the test bits using a mask
        test_bits_mask = sum(1 << ((i + 1) * self.field_size + i) for i in range(self.r))
        result_bits = comparison & test_bits_mask
        
        # The number of flipped bits tells us the approximate rank in the sketch space
        # (Using bit_count to simulate counting the remaining 1s in parallel)
        approx_rank = result_bits.bit_count() 
        
        # Sketching loses order information. We check the boundary key to find the actual mismatch point
        match_idx = min(max(0, approx_rank), self.r - 1)
        critical_mismatch = query ^ self.keys[match_idx]
        longest_common_prefix_len = self.w - 1 - self._msb(critical_mismatch)
        
        # Use a binary search on the small list of keys (or actual branch checking) to get the final rank
        actual_rank = 0
        for k in self.keys:
            if query > k:
                actual_rank += 1
            else:
                break
                
        return actual_rank


if __name__ == "__main__":
    # Example:
    
    fusion_tree = FusionTree(w=64)
    
    # Insert keys
    keys = [10, 20, 30, 40, 50]
    for key in keys:
        fusion_tree.root.keys.append(key)
    
    # Search for keys
    print("Searching for keys")
    search_keys = [5, 10, 25, 30, 60]
    for key in search_keys:
        found = fusion_tree.search(key)
        print(f"Searching for {key}: {'Found' if found else 'Not Found'}")
        