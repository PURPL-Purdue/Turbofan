from abc import abstractmethod, ABC
from pathlib import Path
import yaml

from .Flow import Flow
from .GeometryInterface import GeometryInterface
from .ComponentBase import ComponentBase
from .Compressor import Compressor
from .Turbine import Turbine
from .Display import Display

DEBUG_PATH = Path(__file__).resolve().parent.parent.parent / 'Output' / 'Debug.txt'

class Engine(ABC):
    def __init__(self, name):
        self.name = name
        self.flowpath = {}
        self.shafts = {}

        self.debug_file = DEBUG_PATH

    def build(self, *args) -> None:
        for component in args:
            setattr(self, component.name, component)
            component.engine = self

            if component.type == 'FLOWPATH':
                self.flowpath[component.name] = component
            elif component.type == 'SHAFT':
                self.shafts[component.name] = component
            else:
                raise RuntimeError("engine.build(): Unrecognized component type")

    def config(self, config_file) -> None:
        ComponentBase.load_config(config_file)
        Engine.load_config(config_file)
        for attributeValue in self.__dict__.values():
            if isinstance(attributeValue, ComponentBase):
                attributeValue.config()

    def CYAN(self) -> None:
        try:
            for component in self.flowpath.values():
                component.CYAN()
            self.performance()
        except RuntimeError as error:
            try:
                Disp = Display(self)
                Disp.textOutput(DEBUG_PATH, verbose=True)
            except RuntimeError:
                pass
            raise RuntimeError(error)

    def interface(self, comp1: str, comp2: str, station_name: str) -> None:
        # Shaft interface
        if '.' not in comp2:
            comp = comp1.split('.')[0]
            comp = self.flowpath[comp]
            shaft = self.shafts[comp2]

            comp.Shaft = shaft
            if isinstance(comp, Compressor):
                shaft.consumers.append(comp)
            elif isinstance(comp, Turbine):
                shaft.generators.append(comp)
            else:
                raise RuntimeError("engine.interface(): invalid component type for shaft interface")

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

    @abstractmethod
    def performance(self) -> None:
        pass

    @classmethod
    def load_config(cls, config_file):
        """Loads the configuration YAML file into a python dictionary as a ComponentBase class attribute. This allows for all component objects (that are subclasses of ComponentBase) to freely access all the config information"""
        cls.cfg = yaml.safe_load(config_file.read_text())
        cls.cfg_path = config_file