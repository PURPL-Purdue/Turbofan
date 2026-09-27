import yaml
from abc import ABC, abstractmethod

class ComponentBase(ABC):
    """
    The ComponentBase class is the superclass of all component classes i.e. all component objects are extensions (or extensions of extensions) of the ComponentBase object

    The name attribute of each component (the name ATTRIBUTE, not the name of the instantiated variable) is
    very important in dictating how the object behaves. Please observe the following:
        - The low pressure compressor MUST be named 'LPC'
        - The high pressure compressor MUST be named 'HPC'
        - The high pressure turbine MUST be named 'HPT'
        - The low pressure turbine MUST be named 'LPT'
        - The burner MUST be named 'BURNER'
    """ # TODO: fix this docstring

    @classmethod
    def load_config(cls, config_file):
        """Loads the configuration YAML file into a python dictionary as a ComponentBase class attribute. This allows for all component objects (that are subclasses of ComponentBase) to freely access all the config information"""
        cls.cfg = yaml.safe_load(config_file.read_text())

    def __init__(self, name, component_type):
        from CMYK.Object_Definitions.Components.Turbofan import Engine
        self.name : str = name
        self.type : str = component_type
        self.engine : Engine | None = None

    def _set_Wfactor(self):
        self.Wstream = self.cfg[self.name]['Wstream']
        if self.Wstream == 'FULL':
            self.Wfactor = 1 + self.cfg['FAN']['bypass']
        elif self.Wstream == 'BYPASS':
            self.Wfactor = self.cfg['FAN']['bypass']
        else:
            self.Wfactor = 1

    @abstractmethod
    def config(self):
        pass