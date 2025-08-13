def is_point_in_polygon(point: tuple[float, float], polygon: list[ tuple[float, float] ]) -> bool:
    """
    Returns wether a points is contained in a polygon
    by checking how many times an arbitrary lines crosses the edges of the polygon.
    """
    px, py = point
    inside = False
    n = len(polygon)

    for i in range(n):
        j = (i + 1) % n
        xi, yi = polygon[i]
        xj, yj = polygon[j]

        # Check if point's y is between yi and yj
        if (yi > py) != (yj > py):
            # Find the x coordinate of the intersection of the polygon edge with the horizontal ray
            intersect_x = xi + (py - yi) * (xj - xi) / (yj - yi)

            if px < intersect_x:
                inside = not inside  # toggle the state

    return inside