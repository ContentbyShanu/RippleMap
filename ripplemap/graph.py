from collections import deque

class DependencyGraph:
    """An edge A -> B means A imports B."""
    def __init__(self):
        self.dependencies = {}
        self.dependents = {}

    def add_node(self, node):
        self.dependencies.setdefault(node, set())
        self.dependents.setdefault(node, set())

    def add_edge(self, importer, imported):
        self.add_node(importer)
        self.add_node(imported)
        self.dependencies[importer].add(imported)
        self.dependents[imported].add(importer)

    def direct_dependents(self, changed):
        return sorted(self.dependents.get(changed, set()))

    def reverse_distances(self, changed):
        distances, visited = {}, {changed}
        queue = deque([(changed, 0)])
        while queue:
            node, distance = queue.popleft()
            for dependent in sorted(self.dependents.get(node, set())):
                if dependent not in visited:
                    visited.add(dependent)
                    distances[dependent] = distance + 1
                    queue.append((dependent, distance + 1))
        return distances
