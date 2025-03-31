import heapdict


class MinPriorityQueue:
    """
    Implements a min-priority queue using a heap-based dictionary.
    Supports insertion, extraction of the minimum element, and priority decrease.
    """
    def __init__(self):
        self.heap = heapdict.heapdict()

    def is_empty(self):
        """Checks if the priority queue is empty."""
        return len(self.heap) == 0

    def _insert(self, item, key):
        """Inserts an item with the given priority key."""
        self.heap[item] = key

    def extract_min(self):
        """Removes and returns the item with the smallest key."""
        if not self.heap:
            return None
        min_item, min_key = self.heap.popitem()
        return min_item, min_key

    def decrease_priority(self, item, key):
        """Updates the item's priority if the new key is smaller."""
        if item not in self.heap:
            self._insert(item, key)
        elif key < self.heap[item]:
            self.heap[item] = key


class MaxPriorityQueue:
    """
    Implements a max-priority queue using a heap-based dictionary.
    Supports insertion, extraction of the maximum element, and priority increase.
    """
    def __init__(self):
        self.heap = heapdict.heapdict()

    def is_empty(self):
        """Checks if the priority queue is empty."""
        return len(self.heap) == 0

    def _insert(self, item, key):
        """Inserts an item with the given priority key (stored as negative for max-heap behavior)."""
        self.heap[item] = -key

    def extract_max(self):
        """Removes and returns the item with the highest key."""
        if not self.heap:
            return None
        max_item, neg_max_key = self.heap.popitem()
        return max_item, -neg_max_key

    def increase_priority(self, item, key):
        """Updates the item's priority if the new key is larger."""
        if item not in self.heap:
            self._insert(item, key)
        elif key > -self.heap[item]:
            self.heap[item] = -key
