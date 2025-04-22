import unittest
from src.priority_queue import MinPriorityQueue, MaxPriorityQueue  # Replace 'your_module' with the actual module name


class TestMinPriorityQueue(unittest.TestCase):

    def test_empty_queue(self):
        pq = MinPriorityQueue()
        self.assertTrue(pq.is_empty())
        self.assertIsNone(pq.extract_min())

    def test_decrease_priority_inserts_and_extracts_correctly(self):
        pq = MinPriorityQueue()
        pq.decrease_priority('a', 3)
        pq.decrease_priority('b', 1)
        pq.decrease_priority('c', 2)

        item, key = pq.extract_min()
        self.assertEqual((item, key), ('b', 1))

        item, key = pq.extract_min()
        self.assertEqual((item, key), ('c', 2))

        item, key = pq.extract_min()
        self.assertEqual((item, key), ('a', 3))

        self.assertTrue(pq.is_empty())

    def test_decrease_priority_updates_only_when_smaller(self):
        pq = MinPriorityQueue()
        pq.decrease_priority('x', 10)
        pq.decrease_priority('x', 5)  # should update
        pq.decrease_priority('x', 15)  # should NOT update

        item, key = pq.extract_min()
        self.assertEqual((item, key), ('x', 5))


class TestMaxPriorityQueue(unittest.TestCase):

    def test_empty_queue(self):
        pq = MaxPriorityQueue()
        self.assertTrue(pq.is_empty())
        self.assertIsNone(pq.extract_max())

    def test_increase_priority_inserts_and_extracts_correctly(self):
        pq = MaxPriorityQueue()
        pq.increase_priority('a', 1)
        pq.increase_priority('b', 3)
        pq.increase_priority('c', 2)

        item, key = pq.extract_max()
        self.assertEqual((item, key), ('b', 3))

        item, key = pq.extract_max()
        self.assertEqual((item, key), ('c', 2))

        item, key = pq.extract_max()
        self.assertEqual((item, key), ('a', 1))

        self.assertTrue(pq.is_empty())

    def test_increase_priority_updates_only_when_larger(self):
        pq = MaxPriorityQueue()
        pq.increase_priority('y', 5)
        pq.increase_priority('y', 10)  # should update
        pq.increase_priority('y', 3)   # should NOT update

        item, key = pq.extract_max()
        self.assertEqual((item, key), ('y', 10))


if __name__ == '__main__':
    unittest.main()
