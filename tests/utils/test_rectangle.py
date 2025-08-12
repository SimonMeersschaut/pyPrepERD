import unittest
from utils.rectangle import r1_contains_r2, r1_intersects_r2, r1_contains_point


class TestRectangleContains(unittest.TestCase):
    def test_identical_rectangles(self):
        # r2 is exactly the same size and position as r1 — should be contained
        self.assertTrue(r1_contains_r2((0, 0, 10, 10), (0, 0, 10, 10)))

    def test_r2_inside_r1(self):
        # r2 is fully inside r1 — no touching edges
        self.assertTrue(r1_contains_r2((0, 0, 10, 10), (2, 2, 5, 5)))

    def test_r2_touches_r1_edges(self):
        # r2 is inside r1 and touching edges — still considered "contained"
        self.assertTrue(r1_contains_r2((0, 0, 10, 10), (0, 0, 5, 5)))  # touches top-left corner
        self.assertTrue(r1_contains_r2((0, 0, 10, 10), (5, 5, 5, 5)))  # touches middle area
        self.assertTrue(r1_contains_r2((0, 0, 10, 10), (0, 5, 10, 5))) # spans full width along an edge

    def test_r2_extends_outside_r1(self):
        # Any part of r2 going outside r1 — should return False
        self.assertFalse(r1_contains_r2((0, 0, 10, 10), (-1, 0, 5, 5)))  # extends left
        self.assertFalse(r1_contains_r2((0, 0, 10, 10), (0, 0, 11, 5)))  # extends right
        self.assertFalse(r1_contains_r2((0, 0, 10, 10), (0, 0, 5, 11)))  # extends down
        self.assertFalse(r1_contains_r2((0, 0, 10, 10), (9, 9, 2, 2)))   # bottom-right corner overflow

    def test_negative_coordinates(self):
        # r1 covers area from (-5, -5) to (10, 10)
        self.assertTrue(r1_contains_r2((-5, -5, 15, 15), (0, 0, 5, 5)))    # fully inside positive coords
        self.assertFalse(r1_contains_r2((-5, -5, 15, 15), (-6, -6, 5, 5))) # extends beyond top-left

    def test_zero_sized_rectangles(self):
        # Zero width or height counts as "contained" if its point is inside r1
        self.assertTrue(r1_contains_r2((0, 0, 10, 10), (5, 5, 0, 0)))       # point inside
        self.assertTrue(r1_contains_r2((0, 0, 10, 10), (10, 10, 0, 0)))     # exactly at bottom-right corner
        self.assertFalse(r1_contains_r2((0, 0, 10, 10), (11, 10, 0, 0)))    # point outside


class TestRectangleIntersects(unittest.TestCase):
    def test_identical_rectangles(self):
        # Exact same position and size — definitely intersect
        self.assertTrue(r1_intersects_r2((0, 0, 10, 10), (0, 0, 10, 10)))

    def test_fully_overlapping(self):
        # r2 is entirely inside r1 — should intersect
        self.assertTrue(r1_intersects_r2((0, 0, 10, 10), (2, 2, 5, 5)))

    def test_partial_overlap(self):
        # r2 overlaps part of r1 — should intersect
        self.assertTrue(r1_intersects_r2((0, 0, 10, 10), (8, 8, 5, 5)))

    def test_touching_edges(self):
        # Rectangles touching edges are counted as intersecting
        self.assertTrue(r1_intersects_r2((0, 0, 10, 10), (10, 0, 5, 5)))  # right edge
        self.assertTrue(r1_intersects_r2((0, 0, 10, 10), (0, 10, 5, 5)))  # bottom edge
        self.assertTrue(r1_intersects_r2((0, 0, 10, 10), (-5, 0, 5, 5)))  # left edge
        self.assertTrue(r1_intersects_r2((0, 0, 10, 10), (0, -5, 5, 5)))  # top edge

    def test_touching_corners(self):
        # Touching exactly at a corner still counts as intersecting
        self.assertTrue(r1_intersects_r2((0, 0, 10, 10), (10, 10, 5, 5)))  # bottom-right corner
        self.assertTrue(r1_intersects_r2((0, 0, 10, 10), (-5, -5, 5, 5)))  # top-left corner

    def test_no_overlap(self):
        # No part of the rectangles overlap — should be False
        self.assertFalse(r1_intersects_r2((0, 0, 10, 10), (11, 0, 5, 5)))  # to the right
        self.assertFalse(r1_intersects_r2((0, 0, 10, 10), (0, 11, 5, 5)))  # below
        self.assertFalse(r1_intersects_r2((0, 0, 10, 10), (-6, 0, 5, 5)))  # to the left
        self.assertFalse(r1_intersects_r2((0, 0, 10, 10), (0, -6, 5, 5)))  # above

    def test_zero_sized_rectangles(self):
        # Zero width/height still counts if the point lies within or on the other rectangle
        self.assertTrue(r1_intersects_r2((0, 0, 10, 10), (5, 5, 0, 0)))       # point inside
        self.assertTrue(r1_intersects_r2((0, 0, 10, 10), (10, 10, 0, 0)))     # exactly bottom-right corner
        self.assertFalse(r1_intersects_r2((0, 0, 10, 10), (11, 10, 0, 0)))    # point outside


class TestRectangleContainsPoint(unittest.TestCase):
    def test_point_inside(self):
        # Point well within the rectangle
        self.assertTrue(r1_contains_point((0, 0, 10, 10), (5, 5)))

    def test_point_on_edges(self):
        # Points on the edges are considered inside
        self.assertTrue(r1_contains_point((0, 0, 10, 10), (0, 5)))    # left edge
        self.assertTrue(r1_contains_point((0, 0, 10, 10), (10, 5)))   # right edge
        self.assertTrue(r1_contains_point((0, 0, 10, 10), (5, 0)))    # top edge
        self.assertTrue(r1_contains_point((0, 0, 10, 10), (5, 10)))   # bottom edge

    def test_point_on_corners(self):
        # Points exactly on corners are inside
        self.assertTrue(r1_contains_point((0, 0, 10, 10), (0, 0)))    # top-left
        self.assertTrue(r1_contains_point((0, 0, 10, 10), (10, 0)))   # top-right
        self.assertTrue(r1_contains_point((0, 0, 10, 10), (0, 10)))   # bottom-left
        self.assertTrue(r1_contains_point((0, 0, 10, 10), (10, 10)))  # bottom-right

    def test_point_outside(self):
        # Points outside should return False
        self.assertFalse(r1_contains_point((0, 0, 10, 10), (-1, 5)))   # left
        self.assertFalse(r1_contains_point((0, 0, 10, 10), (11, 5)))   # right
        self.assertFalse(r1_contains_point((0, 0, 10, 10), (5, -1)))   # above
        self.assertFalse(r1_contains_point((0, 0, 10, 10), (5, 11)))   # below

    def test_negative_coordinates(self):
        # Works with negative positions
        self.assertTrue(r1_contains_point((-5, -5, 10, 10), (0, 0)))    # inside
        self.assertFalse(r1_contains_point((-5, -5, 10, 10), (-6, 0)))  # outside to the left

    def test_zero_sized_rectangle(self):
        # Rectangle with zero width and height contains only its single point
        self.assertTrue(r1_contains_point((5, 5, 0, 0), (5, 5)))   # exact point
        self.assertFalse(r1_contains_point((5, 5, 0, 0), (5, 6)))  # outside
