from abc import ABC, abstractmethod

class ComponentBase(ABC):
    """ USAGE NOTES:
    The name attribute of each component (the name ATTRIBUTE, not the name of the instantiated variable) is
    very important in dictating how the object behaves. Please observe the following:
        - The low pressure compressor MUST be named 'LPC'
        - The high pressure compressor MUST be named 'HPC'
        - The high pressure turbine MUST be named 'HPT'
        - The low pressure turbine MUST be named 'LPT'
        - The burner MUST be named 'BURNER'
        - The starting ambient object MUST have a name starting with "FS" (for freestream). Otherwise, it will
          be treated as the end of a flowpath branch.

    """
    def __init__(self, name, component_type):
        from .Engine import Engine # For type checking
        self.name : str = name
        self.type : str = component_type
        self.engine : Engine | None = None

    @abstractmethod
    def config(self, config_file):
        pass