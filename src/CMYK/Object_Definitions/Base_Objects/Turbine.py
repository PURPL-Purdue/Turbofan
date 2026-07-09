from .ComponentBase import ComponentBase

class Turbine(ComponentBase):
    def __init__(self, name, component_type):
        super().__init__(name, component_type)

    def config(self):
        pass