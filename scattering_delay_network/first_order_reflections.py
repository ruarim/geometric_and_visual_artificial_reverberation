def reflect_source(source, room_dim):
    """
    Generate first-order image sources by reflecting the source across each boundary of the room.
    
    Parameters:
    source (tuple): Coordinates of the sound source (x, y, z).
    room_dim (tuple): Dimensions of the room (Lx, Ly, Lz).
    
    Returns:
    list: Coordinates of the first-order image sources.
    """
    x_s, y_s, z_s = source
    Lx, Ly, Lz = room_dim
    
    image_sources = [
        (-x_s, y_s, z_s),        # Reflect across x = 0
        (2*Lx - x_s, y_s, z_s),  # Reflect across x = Lx
        (x_s, -y_s, z_s),        # Reflect across y = 0
        (x_s, 2*Ly - y_s, z_s),  # Reflect across y = Ly
        (x_s, y_s, -z_s),        # Reflect across z = 0
        (x_s, y_s, 2*Lz - z_s)   # Reflect across z = Lz
    ]
    
    return image_sources


def find_intersection(image_source, receiver, boundary_axis, boundary_value):
    """
    Find the intersection of the path from the image source to the receiver with a given boundary.
    
    Parameters:
    image_source (tuple): Coordinates of the image source (x, y, z).
    receiver (tuple): Coordinates of the receiver (x, y, z).
    boundary_axis (str): Axis of the boundary ('x', 'y', 'z').
    boundary_value (float): Value of the boundary along the given axis.
    
    Returns:
    tuple: Coordinates of the reflection point on the boundary.
    """
    x_s, y_s, z_s = image_source
    x_r, y_r, z_r = receiver
    
    if boundary_axis == 'x':
        t = (boundary_value - x_s) / (x_r - x_s)
        y_reflect = y_s + t * (y_r - y_s)
        z_reflect = z_s + t * (z_r - z_s)
        return [boundary_value, y_reflect, z_reflect]
    
    elif boundary_axis == 'y':
        t = (boundary_value - y_s) / (y_r - y_s)
        x_reflect = x_s + t * (x_r - x_s)
        z_reflect = z_s + t * (z_r - z_s)
        return [x_reflect, boundary_value, z_reflect]
    
    elif boundary_axis == 'z':
        t = (boundary_value - z_s) / (z_r - z_s)
        x_reflect = x_s + t * (x_r - x_s)
        y_reflect = y_s + t * (y_r - y_s)
        return [x_reflect, y_reflect, boundary_value]


def find_reflections(room_dim, source, receiver, reflection_order):
    """
    Find the locations of early reflections in a rectangular room.
    
    Parameters:
    source (tuple): Coordinates of the sound source (x, y, z).
    receiver (tuple): Coordinates of the receiver (x, y, z).
    room_dim (tuple): Dimensions of the room (Lx, Ly, Lz).
    
    Returns:
    list: Coordinates of the reflection points.
    """
    image_sources = reflect_source(source, room_dim)
    reflection_points = []
    
    for img_src in image_sources:
        if img_src[0] < 0:
            reflection_points.append(find_intersection(img_src, receiver, 'x', 0))
        elif img_src[0] > room_dim[0]:
            reflection_points.append(find_intersection(img_src, receiver, 'x', room_dim[0]))
        
        if img_src[1] < 0:
            reflection_points.append(find_intersection(img_src, receiver, 'y', 0))
        elif img_src[1] > room_dim[1]:
            reflection_points.append(find_intersection(img_src, receiver, 'y', room_dim[1]))
        
        if img_src[2] < 0:
            reflection_points.append(find_intersection(img_src, receiver, 'z', 0))
        elif img_src[2] > room_dim[2]:
            reflection_points.append(find_intersection(img_src, receiver, 'z', room_dim[2]))
    
    return reflection_points
