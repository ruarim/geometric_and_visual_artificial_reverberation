# defines the geometry of a room
# and its frequency dependant and independant wall absorption coefficients

from utils.point3D import Point3D
from .first_order_reflections import find_reflections

class Room:
    def __init__(self, dims: list[float], source: Point3D, mic: Point3D, reflection_order: int): 
        # only shoebox for now        
        self.dims = dims
        self.valid_shape()
        self.source = source
        self.mic = mic
        self.valid_source_mic()
        er = find_reflections(self.dims, self.source.to_list(), self.mic.to_list(), reflection_order)
        self.early_reflections = [Point3D(r) for r in er]
        
        # wall attenuation values array
        
        # wall filter coefficient array
        
    def valid_shape(self):
        assert all(dim > 0 for dim in self.dims), "invalid room shape"
    
    def valid_source_mic(self):
        assert self.source.less_than(self.dims[0], self.dims[1], self.dims[2])
        assert self.mic.less_than(self.dims[0], self.dims[1], self.dims[2])
    
    def update_reflections(self):
        self.early_reflections = find_reflections(self.dims, self.source)