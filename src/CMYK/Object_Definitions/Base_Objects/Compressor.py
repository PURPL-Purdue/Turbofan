from .ComponentBase import ComponentBase

class Compressor(ComponentBase):
    def __init__(self, name, component_type):
        super().__init__(name, component_type)
        self.pr = None

    def config(self):
        pass