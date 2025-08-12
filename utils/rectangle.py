"""
This file contains helper functions for computations with rectangles.
Rectangles are a tuple of four values: (x0, y0, w, h), where:
    - x0 is the bottom left point's x-coordinate,
    - y0 is the bottom left point's y-coordinate,
    - w is the width of the rectangle, and
    - h is the height of the rectangle.

      (x0, y0 + h) ----- width ------ +
           |                           |
           |                           |
          height                       |
           |                           |
           |                           |
           + ------------------------- +
"""

def r1_contains_r2(rect1: tuple, rect2: tuple) -> bool:
    """
    Returns whether `rect1` fully contains `rect2`.
    We consider equal rectangles to contain each other.
    """
    return (
        rect1[0] <= rect2[0] and
        rect1[1] <= rect2[1]
    ) and (
        rect1[0] + rect1[2] >= rect2[0] + rect2[2] and
        rect1[1] + rect1[3] >= rect2[1] + rect2[3]
    )


def r1_intersects_r2(rect1: tuple, rect2: tuple) -> bool:
    """
    Returns whether `rect1` intersects `rect2` at all.
    Rectangles that just touch at edges or corners are considered intersecting.
    """
    # Extract coordinates
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    # Calculate top-right coordinates
    r1_right = x1 + w1
    r1_top = y1 + h1
    r2_right = x2 + w2
    r2_top = y2 + h2

    # If one rectangle is entirely to the left, right, above, or below the other
    if r1_right < x2 or r2_right < x1:
        return False
    if r1_top < y2 or r2_top < y1:
        return False

    return True


def r1_contains_point(rect1: tuple, point: tuple[float, float]) -> bool:
    """
    Returns whether `rect1` contains the given `point` (x, y).
    Points exactly on the rectangle's edges are considered inside.
    """
    x0, y0, w, h = rect1
    px, py = point

    return (x0 <= px <= x0 + w) and (y0 <= py <= y0 + h)
