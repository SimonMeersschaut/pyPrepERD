"""
QuadTree data structure for efficient spatial partitioning of 2D points.

This module implements a quadtree that recursively subdivides a bounding rectangle
into four quadrants (quads) to organize points in a way that speeds up spatial queries,
such as counting points inside a given area.

Key features:
- Limits recursion depth using MAX_DEPTH to avoid excessive subdivision and Python’s
  recursion depth limit. When MAX_DEPTH is reached, quads store points directly in a list.
- Supports counting the number of points contained within an arbitrary rectangle via
  the `containing_points` method.
- Uses rectangle helper functions from `utils.rectangle`:
    - `r1_contains_r2(rect1, rect2)`: Checks if `rect1` fully contains `rect2`.
    - `r1_intersects_r2(rect1, rect2)`: Checks if `rect1` intersects with `rect2`.

Classes:
- QuadTree: Manages the overall tree structure and root node.
- Quad: Represents an individual node in the tree. Each non-leaf node has four child quads.

Typical usage example:
    qt = QuadTree(0, 0, 100, 100)
    qt.insert(10, 10)
    qt.insert(50, 50)

    count = qt.root.containing_points(0, 0, 30, 30)
    print(count)  # Outputs how many points are inside the rectangle (0, 0, 30, 30)


We use the naming convention `quadrants`, so that we can use analogies with mathematics.
Note that Quadrants are numbered from 1 to 4 in Roman numerals as follows:

                        y
                        ^
             II         |       I
                        |
      ----------------------------------> x
                        |
            III         |       IV
                        |


"""

from utils.rectangle import r1_contains_r2, r1_intersects_r2, r1_contains_point

MAX_DEPTH = 10
# `MAX_DEPTH` defines the maximal depth of the quad tree.
# This is necessary, as there are too many points to construct a
# full quad tree (because of the max recursion depth of python).
# When the max depth is exceeded, the program simply appends
# the point to a list `points` on that leave. We consider quads
# at the max depth as small enough so that it is not computationally
# hard to check all points in that rectangle.


class QuadTree:
    def __init__(
        self,
        rect: tuple[float, float, float, float]
    ):
        # create initial structure
        self.rect: tuple[float, float, float, float] = rect
        self.root: Quad = Quad(rect=rect, depth=0)

    def containing_points(self, rect: tuple[float, float, float, float]):
        return self.root.containing_points(rect)
    
    def insert(self, point: tuple[float, float]):
        self.root.insert(point)


class Quad:
    def __init__(self, rect:tuple[float, float, float, float], depth:int):
        self.depth = depth # depth in 4-way tree, with root the root of the tree
        self.rect = rect
        
        self.count = 0 # number of points, contained by this quad
        self.points: list[tuple[float, float], ] = [] # only used if this quad is a leave in the tree
        # None <=> !leave
        self.children: tuple[Quad] = (None, None, None, None) # each non-leave node has four children
        # self.split_in_four()
    
    def insert(self, point:tuple[float, float]):
        #
        if self.points != None:
            # `this` is a leave
            if self.count == 0:
                # the newly added point will be the only one,
                # so just add it
                self.points = [point]
            else:
                # there will be multiple points in this quad,
                # after this insert operation
                # We should split this quad in four other quads
                # (if allowed by the max_depth).
                if self.depth == MAX_DEPTH:
                    # not allowed to recurse, just add
                    # the point to the list of points
                    self.points.append(point)
                else:
                    # allowed to recurse
                    # split in 4 other quads
                    self._split_in_four()
                    # add point
                    success = False
                    for child in self.children:
                        if r1_contains_point(child.rect, point):
                            child.insert(point)
                            success = True
                            break
                    if not success:
                        raise ValueError("No quadrant found for point.")
        else:
            # insert the point to one of the 
            # four children quads (recursively).
            success = False
            for child in self.children:
                if r1_contains_point(child.rect, point):
                    child.insert(point)
                    success = True
                    break
            if not success:
                raise ValueError("No quadrant found for point.")
        
        self.count += 1
    
    def containing_points(self, rect:tuple[float, float, float, float]) -> int:
        """
        Returns how many points are contained by the given rectangle (x, y, w, h).
        That is, it will search the tree with root `this`, and sum up all the points
        that have been stored under this root, which are also contained by the rectangle (x, y, w, h).
        """
        
        if self.count == 0:
            # no points in this quad
            return 0
        
        if not r1_intersects_r2(rect, self.rect):
            # no intersection, so impossible to contain any points
            return 0
        else:
            if r1_contains_r2(rect, self.rect):
                # selected rectangle contains entire quad
                # thus, all points in quad are selected
                return self.count
            else:
                # Some points might be contained, some might not

                if self.points == None:
                    # not a leave,
                    # check my children quads
                    accumulative = 0
                    for child in self.children:
                        accumulative += child.containing_points(rect)
                    return accumulative
                else:
                    # `this` is a leave,
                    # so check all points
                    accumulative = 0
                    for point in self.points:
                        if r1_contains_point(rect, point):
                            accumulative += 1
                    return accumulative
    
    def _split_in_four(self):
        """
        This function splits the current quad in four
        children quads.
        """
        bottom_left = (self.rect[0], self.rect[1])
        # top_right = (self.rect[0] + self.rect[2], self.rect[1] + self.rect[3])
        center = (self.rect[0] + self.rect[2]/2, self.rect[1] + self.rect[3]/2)

        new_width, new_height = self.rect[2]/2, self.rect[3]/2

        self.children = (
            Quad(   # I
                rect=(
                    center[0],
                    center[1],
                    new_width,
                    new_height,
                ),
                depth=self.depth+1
            ), 
            Quad(   # II
                rect=(
                    bottom_left[0],
                    center[1],
                    new_width,
                    new_height,
                ),
                depth=self.depth+1
            ), 
            Quad(   # III
                rect=(
                    bottom_left[0],
                    bottom_left[1],
                    new_width,
                    new_height,
                ),
                depth=self.depth+1
            ), 
            Quad(   # IV
                rect=(
                    center[0],
                    bottom_left[1],
                    new_width,
                    new_height,
                ),
                depth=self.depth+1
            ), 
        )

        for point in self.points:
            #
            success = False
            for child in self.children:
                if r1_contains_point(child.rect, point):
                    child.insert(point)
                    success = True
                    break
            if not success:
                raise ValueError(f"No quadrant found for point {point}, rect={self.rect}.")
        
        self.points = None