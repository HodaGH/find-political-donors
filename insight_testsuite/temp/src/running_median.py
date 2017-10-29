## Author: Hoda Gholami
## Purpose: -To calculate the running median of contributions using two heaps
## Input: A record from input file
## Output: The running median (whole number format) of contributions so far.
## Assumptions: 
## 	The heaps can be fit into memory


import heapq

class RunningMedian():
    
    def __init__(self):
        self.minheap = []
        self.maxheap = []

    def _balance(self):
        """
        This function make sure that both heaps have same size or with only one node difference

        Parameters
        ----------
        self: two heaps

        Returns
        -------
        void
        """
        if len(self.minheap) - len(self.maxheap) > 1:
            value = heapq.heappop(self.minheap)
            heapq.heappush(self.maxheap, -value)
        elif len(self.maxheap) - len(self.minheap) > 1:
            value = -heapq.heappop(self.maxheap)
            heapq.heappush(self.minheap, value)

    def add(self, value):
        """
        This function add a value to one of these heaps.
        Adding two first values: the first one is added to maxheap,
        the second one is added to maxheap and then the one with greater value will be moved to minheap by balancing
        Adding other values: will be added to the maxheap if it's smaller than its root, otherwise will be added to minheap
        
        Parameters
        ----------
        element: double

        Returns
        -------
        void
        """   
        if not self.minheap or not self.maxheap:
            heapq.heappush(self.maxheap, -value)
            self._balance()
            return
        if value <= -self.maxheap[0]:
            heapq.heappush(self.maxheap, -value)
        else:
            heapq.heappush(self.minheap, value)
        self._balance()

    def get_median(self):
        """
        This function calculates the median.
        If the heaps have same size, median is the mean of their root values
        If Not same size, the median is the root of heap witht more nodes 
        
        Parameters
        ----------
        self: two heaps

        Returns
        ---------
        int
        """ 
        if not self.minheap and not self.maxheap:
            raise IndexError('No median found')

        size = len(self.minheap) + len(self.maxheap)
        if size % 2 == 0:
            return int(round(1.0 * (self.minheap[0] + (-self.maxheap[0])) / 2)) 

        if len(self.minheap) > len(self.maxheap):
            return int(round(self.minheap[0]))
        else:
            return int(round(-self.maxheap[0]))

