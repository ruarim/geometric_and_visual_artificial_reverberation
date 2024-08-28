# contains delay from source to junctions and microphone
from utils.point3D import Point3D
from .propigation_line import PropigationLine

class Source:     
    def __init__(self, location: Point3D):
        self.propigation_lines: list[PropigationLine] = [] # source -> junction
        self.direct_path: PropigationLine = None # source -> mic
        self.location: Point3D = location
    
    def add_to_junction(self, prop_line: PropigationLine):
        self.propigation_lines.append(prop_line)
        
    def add_direct_path(self, prop_line: PropigationLine):
        self.direct_path = prop_line