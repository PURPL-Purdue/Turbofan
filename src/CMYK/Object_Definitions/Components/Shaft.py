import yaml
from pathlib import Path
from CMYK.Object_Definitions.Base_Objects import ComponentBase

class Shaft(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'SHAFT')

        self.RPM = 0
    
    def config(self, configFile: Path) -> None:
        cfg = yaml.safe_load(configFile.read_text())[self.name]

