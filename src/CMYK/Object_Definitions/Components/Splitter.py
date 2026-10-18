from CMYK.Object_Definitions.Base_Objects import ComponentBase

class Splitter(ComponentBase):

    def _init_(self,name):
        super()._init_(name,'SPLIT')

        self.FlowIn = None