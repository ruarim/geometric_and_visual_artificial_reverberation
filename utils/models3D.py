import numpy as np

def parse_obj_file(file_path):
    vertices = []
    current_object = None

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('o '):
                current_object = line.split()[1]
            elif line.startswith('v ') and 'floor' not in current_object: # get vertex and ignore the floor
                parts = line.split()
                vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                vertices.append(vertex)

    return np.array(vertices)

def calculate_dimensions(vertices):
    min_vals = np.min(vertices, axis=0)
    max_vals = np.max(vertices, axis=0)

    dimensions = max_vals - min_vals
    length, height, width = dimensions

    return length, height, width

def get_room_dims(file_path):
    vertices = parse_obj_file(file_path)
    return calculate_dimensions(vertices)
