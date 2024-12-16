class Vector3:
    """Simple 3D Vector representation"""
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = x
        self.y = y
        self.z = z

    def to_dict(self):
        return {"x": self.x, "y": self.y, "z": self.z}

