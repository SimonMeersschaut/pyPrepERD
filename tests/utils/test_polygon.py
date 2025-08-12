from utils import is_point_in_polygon

def test_is_point_in_polygon():
    square = [(0,0), (10,0), (10,10), (0,10)]

    # Inside point
    assert is_point_in_polygon((5,5), square) == True, "Point inside square failed"

    # Outside point
    assert is_point_in_polygon((15,5), square) == False, "Point outside square failed"

    # Point on vertex
    assert is_point_in_polygon((0,0), square) == True, "Point on vertex failed"

    # Point on edge
    assert is_point_in_polygon((5,0), square) == True, "Point on edge failed"

    # Point just outside near edge
    assert is_point_in_polygon((10.1,5), square) == False, "Point just outside failed"

    # Triangle polygon
    triangle = [(0,0), (5,5), (10,0)]
    assert is_point_in_polygon((5,2), triangle) == True, "Point inside triangle failed"
    assert is_point_in_polygon((5,6), triangle) == False, "Point outside triangle failed"

    print("All tests passed!")
