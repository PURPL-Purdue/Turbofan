from .Flow import Flow
from .GeometryInterface import GeometryInterface
from .ComponentBase import ComponentBase
from CMYK.Object_Definitions.Components import Nozzle

class Engine:
    def __init__(self, name):
        self.name = name
        self.flowpath = {}
        self.shafts = {}
    
    def build(self, *args) -> None:
        for component in args:
            setattr(self, component.name, component)
            component.engine = self

            if component.type == 'FLOWPATH':
                self.flowpath[component.name] = component
            elif component.type == 'SHAFT':
                self.shafts[component.name] = component
            else:
                raise RuntimeError("Engine.build(): Unrecognized component type")

    def config(self, config_file) -> None:
        for attributeValue in self.__dict__.values():
            if isinstance(attributeValue, ComponentBase):
                attributeValue.config(config_file)

    def CYAN(self) -> None:
        for component in self.flowpath.values():
            component.CYAN()
        self.performance()
    
    def performance(self):
        for attributeValue in self.__dict__.values():
            if isinstance(attributeValue, Nozzle):
                attributeValue.calcExitVelocity()
                
    
    def interface(self, comp1, comp2, station_name) -> None:
        # Shaft interface
        if '.' not in comp2:
            comp = comp1.split('.')[0]
            comp = self.flowpath[comp]
            shaft = self.shafts[comp2]

            comp.Shaft = shaft

        else:
            # Get the names of both components and attributes
            up_comp, up_flow = comp1.split('.')
            down_comp, down_flow = comp2.split('.')

            up_type = up_flow[0:3]
            down_type = down_flow[0:3]
            if up_type != down_type:
                raise RuntimeError("Interface: port types are mismatched")

            # Extracting/building equivalent geometry port
            up_geo = f'Geo{up_flow[4:]}'
            down_geo = f'Geo{down_flow[4:]}'

            # Convert each component name to the component itself
            up_comp = self.flowpath[up_comp]
            down_comp = self.flowpath[down_comp]

            # Instantiate flows and geometry for the upstream port
            setattr(up_comp, up_flow, Flow(station_name))
            setattr(up_comp, up_geo, GeometryInterface(station_name))
            
            setattr(down_comp, down_flow, getattr(up_comp, up_flow))
            setattr(down_comp, down_geo, getattr(up_comp, up_geo))
        