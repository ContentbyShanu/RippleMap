import unittest
from ripplemap.graph import DependencyGraph

class GraphTests(unittest.TestCase):
    def test_reverse_transitive_distances(self):
        graph = DependencyGraph()
        graph.add_edge("routes", "service")
        graph.add_edge("main", "routes")
        self.assertEqual(graph.reverse_distances("service"), {"routes": 1, "main": 2})

    def test_cycle_terminates(self):
        graph = DependencyGraph()
        graph.add_edge("a", "b")
        graph.add_edge("b", "a")
        self.assertEqual(graph.reverse_distances("a"), {"b": 1})

if __name__ == "__main__":
    unittest.main()
