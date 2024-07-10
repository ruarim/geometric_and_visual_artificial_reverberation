class Point3D:
    def __init__(self, vec3: list[float]): # from list instead makes more sense
        self.x = vec3[0]
        self.y = vec3[1]
        self.z = vec3[2]
    
    def less_than(self, x, y, z):
        return self.x < x and self.y < y and self.z < z
    
    def to_list(self):
        return [self.x, self.y, self.z]