class GeometryInterface:
    
    def __init__(self, type):
        if type == "ANNULAR":
            self.radiusInner : float = None
            self.radiusOuter : float = None
            self.area        : float = None
