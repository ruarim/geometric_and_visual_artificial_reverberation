from math import sqrt
from utils.point3D import Point3D

# get the euclidean distance between a start and end point
def euclid_dist(start: Point3D, end: Point3D):
    diff = vector_diff(start, end)
    distance = sqrt(diff.x**2 + diff.y**2 + diff.z**2)
    return distance

# convert the distance to a delay(ms)
def distance_to_delay(distance, c):
    return (distance / c)
    
def vector_diff(point_a: Point3D, point_b: Point3D): 
    x_diff = point_a.x - point_b.x
    y_diff = point_a.y - point_b.y
    z_diff = point_a.z - point_b.z
    return Point3D([x_diff, y_diff, z_diff])