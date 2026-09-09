from .BladeSlice import BladeSlice

class Blade:
    def __init__(self, name):
        self.name = name
        self.slices: list[BladeSlice] = []
