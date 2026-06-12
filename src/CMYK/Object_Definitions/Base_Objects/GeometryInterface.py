class GeometryInterface:
    
    def __init__(self, type):
        if type == "ANNULAR":
            self.radiusInner = None
            self.radiusOuter = None
            self.area = ( self.radiusOuter**2 - self.radiusInner**2 )
