import challenge
import unittest


class TestIsInBounds(unittest.TestCase):
    # Tests the is_in_bounds fn for a given location input.

    def test_inside(self):
        # tests when a location is inside the polygon
        position = [0.5, 0.5]
        bounds = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
        self.assertTrue(challenge.is_in_bounds(
            position[0], position[1], bounds))

    def test_outside(self):
        # tests when a location is outise the polygon
        position = [2.0, 2.0]
        bounds = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
        self.assertFalse(challenge.is_in_bounds(
            position[0], position[1], bounds))

    def test_boundry(self):
        # tests when a location is location on a boundry
        position = [0.0, 0.7]
        bounds = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
        self.assertTrue(challenge.is_in_bounds(
            position[0], position[1], bounds))

    def test_vertex(self):
        # tests when a location is a vertex of the boundry
        position = [0.0, 1.0]
        bounds = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
        self.assertTrue(challenge.is_in_bounds(
            position[0], position[1], bounds))

    def test_irregular_polygon_in(self):
        # tests when the location is in a compliated, irregular polygon
        position = [3.0, 3.0]
        bounds = [[1.0, 1.0], [2.0, 4.0], [3.0, 5.0], [
            6.0, 3.0], [5.0, 2.0], [4.0, 3.0], [3.0, 2.0]]
        self.assertTrue(challenge.is_in_bounds(
            position[0], position[1], bounds))


if __name__ == '__main__':
    unittest.main()
